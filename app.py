from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Dict, Optional, Tuple

import pandas as pd
import streamlit as st
from PIL import Image

import gspread
from google.oauth2 import service_account


# ============================================================
# CONFIG
# ============================================================
SHEET_ID = "1sfbjEtd-dCZBQPBHG04Rqsxg2hNc24OmUM1cQnQKiIk"

TAB_ATTENDANCE = "Attendance"
TAB_GUESTS = "New Guests"
TAB_NEXT_STEPS = "Next Steps"

LOGO_PATH = "assets/keeptrek_logo.png"


PALETTE = {
    "navy": "#054063",
    "teal": "#179171",
    "green": "#34a94d",
    "blue_gray": "#47919e",
    "muted": "#6b7280",
    "bg_top": "#f7fbfd",
    "bg_mid": "#f4f8fa",
    "bg_bot": "#fdfefd",
}


# ============================================================
# PAGE ROUTER
# ============================================================
if "page" not in st.session_state:
    st.session_state.page = "dashboard"


def go(page: str) -> None:
    st.session_state.page = page
    st.rerun()


# ============================================================
# UI / STYLE
# ============================================================
def configure_page() -> None:
    st.set_page_config(page_title="KeepTrek Dashboard", layout="wide", page_icon="📊")

    st.markdown(
        f"""
        <style>
        :root {{
          --kt-navy: {PALETTE['navy']};
          --kt-teal: {PALETTE['teal']};
          --kt-green: {PALETTE['green']};
          --kt-blue-gray: {PALETTE['blue_gray']};
          --kt-muted: {PALETTE['muted']};
        }}

        body {{
          background: linear-gradient(180deg, {PALETTE['bg_top']} 0%, {PALETTE['bg_mid']} 45%, {PALETTE['bg_bot']} 100%);
          color: var(--kt-navy);
        }}

        h1, h2, h3, h4, h5, h6 {{
          color: var(--kt-navy);
          letter-spacing: -0.02em;
        }}

        .block-container {{
          padding-top: 1.2rem;
          padding-bottom: 2.2rem;
        }}

        .kt-card-title {{
          margin-bottom: 6px;
          color: var(--kt-navy);
        }}

        .kt-subtle {{
          color: var(--kt-blue-gray);
          font-weight: 700;
        }}

        .stButton > button {{
          background: linear-gradient(135deg, var(--kt-teal), var(--kt-green));
          color: white;
          border: none;
          border-radius: 10px;
          font-weight: 900;
          box-shadow: 0 2px 10px rgba(5, 64, 99, 0.18);
          padding: 0.65rem 0.95rem;
        }}

        .stButton > button:hover {{
          background: linear-gradient(135deg, var(--kt-green), var(--kt-teal));
          box-shadow: 0 6px 16px rgba(5, 64, 99, 0.18);
        }}

        .stButton > button:focus {{
          outline: 2px solid var(--kt-blue-gray);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    spacer_left, center, spacer_right = st.columns([1, 2, 1])

    with center:
        try:
            logo = Image.open(LOGO_PATH)
            st.image(logo, width=720)  # big logo
        except Exception:
            st.markdown("### KeepTrek (logo missing)")

        st.markdown(
            """
            <p class="kt-subtle" style="text-align:center; margin-top: 6px;">
              Measuring Meaningful Metrics
            </p>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# GOOGLE SHEETS CONNECT
# ============================================================
def get_gspread_client() -> gspread.Client:
    creds = service_account.Credentials.from_service_account_info(
        dict(st.secrets["google"]),
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ],
    )
    return gspread.authorize(creds)


@st.cache_data(ttl=60)
def load_tab_as_df(sheet_id: str, tab_name: str) -> pd.DataFrame:
    gc = get_gspread_client()
    sh = gc.open_by_key(sheet_id)
    ws = sh.worksheet(tab_name)

    values = ws.get_all_values()
    if not values or len(values) < 2:
        return pd.DataFrame()

    headers = values[0]
    rows = values[1:]
    df = pd.DataFrame(rows, columns=headers)
    return df


# ============================================================
# METRICS LOGIC
# ============================================================
@dataclass(frozen=True)
class Window:
    label: str
    days: int


WINDOWS = [
    Window("Last Week", 7),
    Window("Last 30 Days", 30),
    Window("Last Quarter", 90),   # simple rolling quarter
    Window("Last 90 Days", 90),
    Window("One Year Snapshot", 365),
]


def _parse_date_series(s: pd.Series) -> pd.Series:
    # Accepts "YYYY-MM-DD" mostly, but tries hard.
    return pd.to_datetime(s, errors="coerce").dt.date


def _trend_pct(current: float, previous: float) -> str:
    if previous is None or previous == 0:
        return "N/A"
    pct = ((current - previous) / previous) * 100.0
    sign = "+" if pct >= 0 else ""
    return f"{sign}{pct:.1f}%"


def _trend_arrow(change: str) -> str:
    c = (change or "").strip()
    if c == "N/A":
        return "—"
    if c.startswith("-"):
        return "↓"
    if c.startswith("+"):
        return "↑"
    return "→"


def _trend_color(change: str) -> str:
    c = (change or "").strip()
    if c == "N/A":
        return PALETTE["blue_gray"]
    if c.startswith("-"):
        return PALETTE["navy"]
    if c.startswith("+"):
        return PALETTE["green"]
    return PALETTE["muted"]


def compute_attendance_metrics(df: pd.DataFrame) -> Dict[str, Tuple[int, str]]:
    """
    Expected Attendance columns:
      - Date
      - Service (or Service Name)
      - Attendance (numeric)
    """
    if df.empty:
        return {w.label: (0, "N/A") for w in WINDOWS}

    # Try common column names
    date_col = next((c for c in df.columns if c.strip().lower() in ["date", "service date"]), None)
    att_col = next((c for c in df.columns if c.strip().lower() in ["attendance", "total attendance"]), None)

    if not date_col or not att_col:
        return {w.label: (0, "N/A") for w in WINDOWS}

    df = df.copy()
    df[date_col] = _parse_date_series(df[date_col])
    df[att_col] = pd.to_numeric(df[att_col], errors="coerce").fillna(0)

    today = date.today()
    out: Dict[str, Tuple[int, str]] = {}

    for w in WINDOWS:
        start = today - timedelta(days=w.days)
        prev_start = today - timedelta(days=w.days * 2)
        prev_end = start

        cur = df[(df[date_col] >= start) & (df[date_col] <= today)][att_col].sum()
        prev = df[(df[date_col] >= prev_start) & (df[date_col] < prev_end)][att_col].sum()

        change = "N/A" if prev == 0 else _trend_pct(cur, prev)
        out[w.label] = (int(cur), change)

    return out


def compute_guest_metrics(df: pd.DataFrame) -> Dict[str, Tuple[int, str]]:
    """
    Expected Guests columns include a date column:
      - Visit Date (or Date)
    Metric = number of guest rows in window
    """
    if df.empty:
        return {w.label: (0, "N/A") for w in WINDOWS}

    date_col = next((c for c in df.columns if c.strip().lower() in ["visit date", "date"]), None)
    if not date_col:
        return {w.label: (0, "N/A") for w in WINDOWS}

    df = df.copy()
    df[date_col] = _parse_date_series(df[date_col])

    today = date.today()
    out: Dict[str, Tuple[int, str]] = {}

    for w in WINDOWS:
        start = today - timedelta(days=w.days)
        prev_start = today - timedelta(days=w.days * 2)
        prev_end = start

        cur = df[(df[date_col] >= start) & (df[date_col] <= today)].shape[0]
        prev = df[(df[date_col] >= prev_start) & (df[date_col] < prev_end)].shape[0]

        change = "N/A" if prev == 0 else _trend_pct(cur, prev)
        out[w.label] = (int(cur), change)

    return out


def compute_next_steps_metrics(df: pd.DataFrame) -> Dict[str, Tuple[int, str]]:
    """
    Expected Next Steps columns include:
      - Date
    Metric = number of rows in window (simple) OR count of checked boxes.
    For now: rows count (commitments).
    """
    if df.empty:
        return {w.label: (0, "N/A") for w in WINDOWS}

    date_col = next((c for c in df.columns if c.strip().lower() in ["date", "service date", "visit date"]), None)
    if not date_col:
        return {w.label: (0, "N/A") for w in WINDOWS}

    df = df.copy()
    df[date_col] = _parse_date_series(df[date_col])

    today = date.today()
    out: Dict[str, Tuple[int, str]] = {}

    for w in WINDOWS:
        start = today - timedelta(days=w.days)
        prev_start = today - timedelta(days=w.days * 2)
        prev_end = start

        cur = df[(df[date_col] >= start) & (df[date_col] <= today)].shape[0]
        prev = df[(df[date_col] >= prev_start) & (df[date_col] < prev_end)].shape[0]

        change = "N/A" if prev == 0 else _trend_pct(cur, prev)
        out[w.label] = (int(cur), change)

    return out


# ============================================================
# CARDS
# ============================================================
def render_hero_metric(value: int, change: str) -> None:
    st.markdown(
        f"""
        <div style="display:flex; align-items:baseline; gap:14px;">
          <div style="font-size:54px; font-weight:950; line-height:1; color: var(--kt-navy);">{value}</div>
          <div style="font-size:16px; font-weight:950; color:{_trend_color(change)};">
            {_trend_arrow(change)} {change}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_row(label: str, value: int, change: str) -> None:
    st.markdown(
        f"""
        <div style="display:flex; justify-content:space-between; align-items:center; padding:6px 0;">
          <div style="font-weight:800; color: var(--kt-navy);">{label}</div>
          <div style="font-weight:900; color:{_trend_color(change)};">
            {value} &nbsp; {_trend_arrow(change)} {change}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(title: str, metrics: Dict[str, Tuple[int, str]], add_page: str, key_prefix: str) -> None:
    with st.container(border=True):
        st.markdown(f"<h3 class='kt-card-title'>{title}</h3>", unsafe_allow_html=True)

        hero_value, hero_change = metrics.get("Last Week", (0, "N/A"))
        render_hero_metric(hero_value, hero_change)

        st.divider()

        for w in WINDOWS[1:]:
            v, c = metrics.get(w.label, (0, "N/A"))
            render_metric_row(w.label, v, c)

        st.divider()

        col_a, col_b = st.columns(2)
        with col_a:
            st.button(
                "➕ Add New Data",
                use_container_width=True,
                key=f"{key_prefix}_add",
                on_click=go,
                args=(add_page,),
            )
        with col_b:
            if st.button("🔄 Refresh", use_container_width=True, key=f"{key_prefix}_refresh"):
                st.cache_data.clear()
                st.rerun()


# ============================================================
# PAGES
# ============================================================
def dashboard_page() -> None:
    render_header()

    # Load data
    df_att = load_tab_as_df(SHEET_ID, TAB_ATTENDANCE)
    df_gst = load_tab_as_df(SHEET_ID, TAB_GUESTS)
    df_nst = load_tab_as_df(SHEET_ID, TAB_NEXT_STEPS)

    att_metrics = compute_attendance_metrics(df_att)
    gst_metrics = compute_guest_metrics(df_gst)
    nst_metrics = compute_next_steps_metrics(df_nst)

    col1, col2, col3 = st.columns(3)
    with col1:
        metric_card("Church Attendance", att_metrics, "add_attendance", "attendance")
    with col2:
        metric_card("New Guests", gst_metrics, "add_guests", "guests")
    with col3:
        metric_card("Next Steps", nst_metrics, "add_next_steps", "next_steps")

    st.divider()

    with st.container(border=True):
        st.markdown(
            """
            <div style="opacity:0.75;">
              <h3 style="margin-bottom:6px;">🩺 Church Health Dashboard</h3>
              <p style="margin-top:0; color:var(--kt-blue-gray); font-weight:700;">Coming Soon</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def stub_add_page(title: str, description: str) -> None:
    render_header()
    st.subheader(title)
    st.write(description)

    st.markdown("---")
    st.button("⬅ Return Home", use_container_width=True, on_click=go, args=("dashboard",))

    st.markdown("### Quick Jump")
    c1, c2, c3 = st.columns(3)
    c1.button("Attendance", use_container_width=True, on_click=go, args=("add_attendance",), key=f"jump_att_{title}")
    c2.button("Guests", use_container_width=True, on_click=go, args=("add_guests",), key=f"jump_gst_{title}")
    c3.button("Next Steps", use_container_width=True, on_click=go, args=("add_next_steps",), key=f"jump_nst_{title}")


def router() -> None:
    page = st.session_state.page

    if page == "dashboard":
        dashboard_page()
    elif page == "add_attendance":
        stub_add_page("➕ Add Church Attendance", "Placeholder page. We’ll build the attendance form next.")
    elif page == "add_guests":
        stub_add_page("➕ Add New Guest", "Placeholder page. We’ll build the guest form + scan flow next.")
    elif page == "add_next_steps":
        stub_add_page("➕ Add Next Steps", "Placeholder page. We’ll build next steps + checkboxes next.")
    else:
        st.session_state.page = "dashboard"
        st.rerun()


# ============================================================
# MAIN
# ============================================================
def main() -> None:
    configure_page()
    router()


if __name__ == "__main__":
    main()
