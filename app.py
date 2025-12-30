from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Dict, Tuple

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
TAB_GUESTS = "New_Guests"
TAB_NEXT_STEPS = "Next_Steps"

LOGO_PATH = "assets/keeptrek_logo.png"


# ============================================================
# PAGE ROUTING
# ============================================================
if "page" not in st.session_state:
    st.session_state.page = "dashboard"


def go(page: str) -> None:
    st.session_state.page = page
    st.rerun()


# ============================================================
# THEME
# ============================================================
PALETTE = {
    "navy": "#054063",
    "teal": "#179171",
    "green": "#34a94d",
    "blue_gray": "#47919e",
    "muted": "#6b7280",
}


def configure_page() -> None:
    st.set_page_config(page_title="KeepTrek Dashboard", layout="wide", page_icon="📊")

    st.markdown(
        f"""
        <style>
        body {{
          background: linear-gradient(180deg, #f7fbfd 0%, #f4f8fa 45%, #fdfefd 100%);
          color: {PALETTE['navy']};
        }}

        h1, h2, h3 {{
          letter-spacing: -0.02em;
        }}

        .stButton > button {{
          background: linear-gradient(135deg, {PALETTE['teal']}, {PALETTE['green']});
          color: white;
          font-weight: 900;
          border-radius: 10px;
          padding: 0.6rem 1rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# HEADER
# ============================================================
def render_header() -> None:
    _, center, _ = st.columns([1, 2, 1])

    with center:
        logo = Image.open(LOGO_PATH)
        st.image(logo, width=720)
        st.markdown(
            "<p style='text-align:center;color:#47919e;font-weight:700;'>Measuring Meaningful Metrics</p>",
            unsafe_allow_html=True,
        )


# ============================================================
# GOOGLE SHEETS
# ============================================================
def gs_client():
    creds = service_account.Credentials.from_service_account_info(
        dict(st.secrets["google"]),
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ],
    )
    return gspread.authorize(creds)


@st.cache_data(ttl=60)
def load_sheet(tab_name: str) -> pd.DataFrame:
    gc = gs_client()
    ws = gc.open_by_key(SHEET_ID).worksheet(tab_name)
    rows = ws.get_all_values()
    return pd.DataFrame(rows[1:], columns=rows[0]) if len(rows) > 1 else pd.DataFrame()


# ============================================================
# METRICS
# ============================================================
@dataclass(frozen=True)
class Window:
    label: str
    days: int


WINDOWS = [
    Window("Last Week", 7),
    Window("Last 30 Days", 30),
    Window("Last Quarter", 90),
    Window("Last 90 Days", 90),
    Window("One Year Snapshot", 365),
]


def parse_dates(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce").dt.date


def pct_change(cur: int, prev: int) -> str:
    if prev == 0:
        return "N/A"
    pct = ((cur - prev) / prev) * 100
    return f"{'+' if pct >= 0 else ''}{pct:.1f}%"


def trend_arrow(change: str) -> str:
    if change == "N/A":
        return "—"
    return "↑" if change.startswith("+") else "↓"


def trend_color(change: str) -> str:
    if change == "N/A":
        return PALETTE["blue_gray"]
    return PALETTE["green"] if change.startswith("+") else PALETTE["navy"]


# ============================================================
# METRIC COMPUTERS
# ============================================================
def attendance_metrics(df: pd.DataFrame) -> Dict[str, Tuple[int, str]]:
    df = df.copy()
    df["Date"] = parse_dates(df["Date"])
    df["Attendance Count"] = pd.to_numeric(df["Attendance Count"], errors="coerce").fillna(0)

    today = date.today()
    out = {}

    for w in WINDOWS:
        cur = df[(df["Date"] >= today - timedelta(days=w.days))]["Attendance Count"].sum()
        prev = df[
            (df["Date"] < today - timedelta(days=w.days)) &
            (df["Date"] >= today - timedelta(days=w.days * 2))
        ]["Attendance Count"].sum()

        out[w.label] = (int(cur), pct_change(cur, prev))

    return out


def count_rows_metrics(df: pd.DataFrame, date_col: str) -> Dict[str, Tuple[int, str]]:
    df = df.copy()
    df[date_col] = parse_dates(df[date_col])
    today = date.today()
    out = {}

    for w in WINDOWS:
        cur = df[df[date_col] >= today - timedelta(days=w.days)].shape[0]
        prev = df[
            (df[date_col] < today - timedelta(days=w.days)) &
            (df[date_col] >= today - timedelta(days=w.days * 2))
        ].shape[0]

        out[w.label] = (cur, pct_change(cur, prev))

    return out


# ============================================================
# UI COMPONENTS
# ============================================================
def hero(value: int, change: str):
    st.markdown(
        f"""
        <div style="display:flex;gap:14px;align-items:baseline;">
          <div style="font-size:54px;font-weight:900;">{value}</div>
          <div style="font-weight:900;color:{trend_color(change)};">
            {trend_arrow(change)} {change}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_row(label: str, value: int, change: str):
    st.markdown(
        f"""
        <div style="display:flex;justify-content:space-between;">
          <b>{label}</b>
          <span style="color:{trend_color(change)};">{value} {trend_arrow(change)} {change}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(title: str, metrics: Dict[str, Tuple[int, str]], add_page: str, key: str):
    with st.container(border=True):
        st.subheader(title)
        hero(*metrics["Last Week"])
        st.divider()

        for w in WINDOWS[1:]:
            metric_row(w.label, *metrics[w.label])

        st.divider()
        c1, c2 = st.columns(2)
        c1.button("➕ Add New Data", on_click=go, args=(add_page,), key=f"{key}_add")
        if c2.button("🔄 Refresh", key=f"{key}_refresh"):
            st.cache_data.clear()
            st.rerun()


# ============================================================
# PAGES
# ============================================================
def dashboard():
    render_header()

    df_att = load_sheet(TAB_ATTENDANCE)
    df_gst = load_sheet(TAB_GUESTS)
    df_ns = load_sheet(TAB_NEXT_STEPS)

    col1, col2, col3 = st.columns(3)

    with col1:
        metric_card("Church Attendance", attendance_metrics(df_att), "add_attendance", "att")
    with col2:
        metric_card("New Guests", count_rows_metrics(df_gst, "Visit Date"), "add_guests", "gst")
    with col3:
        metric_card("Next Steps", count_rows_metrics(df_ns, "Date"), "add_next_steps", "ns")

    st.divider()
    st.info("🩺 Church Health Dashboard — Coming Soon")


def stub_page(title: str):
    render_header()
    st.subheader(title)
    st.write("This page will be built next.")
    st.button("⬅ Return Home", on_click=go, args=("dashboard",))


# ============================================================
# MAIN ROUTER
# ============================================================
def main():
    configure_page()

    if st.session_state.page == "dashboard":
        dashboard()
    elif st.session_state.page == "add_attendance":
        stub_page("➕ Add Attendance")
    elif st.session_state.page == "add_guests":
        stub_page("➕ Add New Guest")
    elif st.session_state.page == "add_next_steps":
        stub_page("➕ Add Next Steps")
    else:
        go("dashboard")


if __name__ == "__main__":
    main()
