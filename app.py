from typing import Dict, Tuple

import streamlit as st
from PIL import Image

# ============================================================
# Types
# ============================================================
MetricValue = Tuple[int, str]
MetricStore = Dict[str, Dict[str, MetricValue]]

# ============================================================
# Theme
# ============================================================
PALETTE = {
    "navy": "#054063",
    "teal": "#179171",
    "green": "#34a94d",
    "blue_gray": "#47919e",
    "muted": "#6b7280",
}

# ============================================================
# Time Ranges
# ============================================================
TIME_RANGES = [
    "Last Week",
    "Last 30 Days",
    "Last Quarter",
    "Last 90 Days",
    "One Year Snapshot",
]
HERO_TIME_RANGE = TIME_RANGES[0]

# ============================================================
# Mock Data (swap later for Sheets)
# ============================================================
MOCK_DATA: MetricStore = {
    "attendance": {
        "Last Week": (248, "+4.2%"),
        "Last 30 Days": (982, "+1.1%"),
        "Last Quarter": (2901, "-0.6%"),
        "Last 90 Days": (2875, "N/A"),
        "One Year Snapshot": (11234, "+6.4%"),
    },
    "guests": {
        "Last Week": (21, "+10%"),
        "Last 30 Days": (78, "+3%"),
        "Last Quarter": (212, "-2%"),
        "Last 90 Days": (201, "N/A"),
        "One Year Snapshot": (865, "+8%"),
    },
    "next_steps": {
        "Last Week": (14, "+5%"),
        "Last 30 Days": (63, "+2%"),
        "Last Quarter": (188, "+1%"),
        "Last 90 Days": (179, "N/A"),
        "One Year Snapshot": (742, "+4%"),
    },
}


# ============================================================
# Page + Global Styling
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

        .block-container {{
          padding-top: 1.25rem;
          padding-bottom: 2.25rem;
        }}

        body {{
          background: linear-gradient(180deg, #f7fbfd 0%, #f4f8fa 45%, #fdfefd 100%);
          color: var(--kt-navy);
        }}

        h1, h2, h3, h4, h5, h6 {{
          color: var(--kt-navy);
          letter-spacing: -0.02em;
        }}

        .kt-card-title {{
          margin-bottom: 6px;
          color: var(--kt-navy);
        }}

        /* Buttons: glossy-ish gradient */
        .stButton > button {{
          background: linear-gradient(135deg, var(--kt-teal), var(--kt-green));
          color: white;
          border: none;
          border-radius: 8px;
          font-weight: 800;
          box-shadow: 0 2px 8px rgba(5, 64, 99, 0.18);
          padding: 0.6rem 0.9rem;
        }}

        .stButton > button:hover {{
          background: linear-gradient(135deg, var(--kt-green), var(--kt-teal));
          box-shadow: 0 6px 14px rgba(5, 64, 99, 0.18);
        }}

        .stButton > button:focus {{
          outline: 2px solid var(--kt-blue-gray);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# Header
# ============================================================
def render_header() -> None:
    logo = Image.open("assets/keeptrek_logo.png")

    col1, col2 = st.columns([1.4, 6])
    with col1:
        st.image(logo, width=200)
    with col2:
        st.markdown(
            """
            <div style="line-height:1.05;">
              <h1 style="margin-bottom:0;">KeepTrek</h1>
              <p style="color: var(--kt-blue-gray); margin-top: 6px; font-weight:600;">
                Turning attendance into insight
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# Trend Helpers
# ============================================================
def trend_arrow(change: str) -> str:
    normalized = (change or "").strip()
    if normalized == "N/A":
        return "—"
    if normalized.startswith("-"):
        return "↓"
    if normalized.startswith("+"):
        return "↑"
    return "→"


def trend_color(change: str) -> str:
    normalized = (change or "").strip()
    if normalized == "N/A":
        return PALETTE["blue_gray"]
    if normalized.startswith("-"):
        return PALETTE["navy"]
    if normalized.startswith("+"):
        return PALETTE["green"]
    return PALETTE["muted"]


# ============================================================
# UI Rendering
# ============================================================
def render_metric_row(label: str, value: int, change: str) -> None:
    st.markdown(
        f"""
        <div style="display:flex; justify-content:space-between; align-items:center; padding:6px 0;">
          <div style="font-weight:700; color: var(--kt-navy);">{label}</div>
          <div style="font-weight:800; color:{trend_color(change)};">
            {value} &nbsp; {trend_arrow(change)} {change}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_hero_metric(value: int, change: str) -> None:
    st.markdown(
        f"""
        <div style="display:flex; align-items:baseline; gap:14px;">
          <div style="font-size:52px; font-weight:900; line-height:1; color: var(--kt-navy);">
            {value}
          </div>
          <div style="font-size:16px; font-weight:900; color:{trend_color(change)};">
            {trend_arrow(change)} {change}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(title: str, data_key: str, key_prefix: str) -> None:
    with st.container(border=True):
        st.markdown(f"<h3 class='kt-card-title'>{title}</h3>", unsafe_allow_html=True)

        hero_value, hero_change = MOCK_DATA[data_key][HERO_TIME_RANGE]
        render_hero_metric(hero_value, hero_change)

        st.divider()

        for label in TIME_RANGES[1:]:
            value, change = MOCK_DATA[data_key][label]
            render_metric_row(label, value, change)

        st.divider()

        col_a, col_b = st.columns(2)
        with col_a:
            st.button("➕ Add New Data", key=f"{key_prefix}_add_new_data", use_container_width=True)
        with col_b:
            st.button("🔄 Refresh", key=f"{key_prefix}_refresh", use_container_width=True)


def render_layout() -> None:
    render_header()

    col1, col2, col3 = st.columns(3)
    with col1:
        metric_card("Church Attendance", "attendance", "attendance_card")
    with col2:
        metric_card("New Guests", "guests", "guests_card")
    with col3:
        metric_card("Next Steps", "next_steps", "next_steps_card")

    st.divider()

    with st.container(border=True):
        st.markdown(
            """
            <div style="opacity:0.7;">
              <h3 style="margin-bottom:6px;">🩺 Church Health Dashboard</h3>
              <p style="margin-top:0; color: var(--kt-blue-gray); font-weight:600;">Coming Soon</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# Main
# ============================================================
def main() -> None:
    configure_page()
    render_layout()


if __name__ == "__main__":
    main()
