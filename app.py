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
# Mock Data
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
# Navigation State
# ============================================================
if "page" not in st.session_state:
    st.session_state.page = "dashboard"


def go(page: str) -> None:
    st.session_state.page = page
    st.rerun()

# ============================================================
# Page Config + Styling
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
          background: linear-gradient(180deg, #f7fbfd 0%, #f4f8fa 45%, #fdfefd 100%);
          color: var(--kt-navy);
        }}

        h1, h2, h3 {{
          color: var(--kt-navy);
          letter-spacing: -0.02em;
        }}

        .stButton > button {{
          background: linear-gradient(135deg, var(--kt-teal), var(--kt-green));
          color: white;
          border: none;
          border-radius: 8px;
          font-weight: 800;
          padding: 0.65rem 1rem;
          box-shadow: 0 4px 10px rgba(5,64,99,.18);
        }}

        .stButton > button:hover {{
          background: linear-gradient(135deg, var(--kt-green), var(--kt-teal));
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

    _, center, _ = st.columns([1, 2, 1])
    with center:
        st.image(logo, width=720)
        st.markdown(
            """
            <p style="text-align:center; font-weight:700; color:var(--kt-blue-gray); margin-top:8px;">
                Measuring Meaningful Metrics
            </p>
            """,
            unsafe_allow_html=True,
        )

# ============================================================
# Trend Helpers
# ============================================================
def trend_arrow(change: str) -> str:
    if change == "N/A":
        return "—"
    if change.startswith("-"):
        return "↓"
    if change.startswith("+"):
        return "↑"
    return "→"


def trend_color(change: str) -> str:
    if change == "N/A":
        return PALETTE["blue_gray"]
    if change.startswith("-"):
        return PALETTE["navy"]
    if change.startswith("+"):
        return PALETTE["green"]
    return PALETTE["muted"]

# ============================================================
# Metric Card
# ============================================================
def metric_card(title: str, data_key: str) -> None:
    with st.container(border=True):
        st.subheader(title)

        hero_value, hero_change = MOCK_DATA[data_key][HERO_TIME_RANGE]

        st.markdown(
            f"""
            <div style="display:flex; align-items:baseline; gap:14px;">
              <div style="font-size:54px; font-weight:900;">{hero_value}</div>
              <div style="font-weight:900; color:{trend_color(hero_change)};">
                {trend_arrow(hero_change)} {hero_change}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        for label in TIME_RANGES[1:]:
            v, c = MOCK_DATA[data_key][label]
            st.markdown(
                f"""
                <div style="display:flex; justify-content:space-between;">
                  <div style="font-weight:700;">{label}</div>
                  <div style="font-weight:800; color:{trend_color(c)};">
                    {v} {trend_arrow(c)} {c}
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            st.button(
                "➕ Add New Data",
                key=f"add_btn_{data_key}",
                use_container_width=True,
                on_click=go,
                args=(f"add_{data_key}",),
            )
        with col2:
            st.button(
                "🔄 Refresh",
                key=f"refresh_btn_{data_key}",
                use_container_width=True,
            )

# ============================================================
# Dashboard Page
# ============================================================
def dashboard() -> None:
    render_header()

    col1, col2, col3 = st.columns(3)
    with col1:
        metric_card("Church Attendance", "attendance")
    with col2:
        metric_card("New Guests", "guests")
    with col3:
        metric_card("Next Steps", "next_steps")

    st.divider()

    with st.container(border=True):
        st.markdown(
            """
            <h3>🩺 Church Health Dashboard</h3>
            <p style="color:var(--kt-blue-gray); font-weight:600;">Coming Soon</p>
            """,
            unsafe_allow_html=True,
        )

# ============================================================
# Add Pages
# ============================================================
def add_page(title: str) -> None:
    render_header()
    st.subheader(title)

    with st.form("entry_form"):
        st.date_input("Date")
        st.number_input("Count", min_value=0, step=1)
        st.text_area("Notes")
        submitted = st.form_submit_button("Save Entry", use_container_width=True)

    if submitted:
        st.success("Saved (mock). Data hookup coming soon.")

    st.divider()
    st.button("⬅ Return Home", on_click=go, args=("dashboard",), use_container_width=True)

# ============================================================
# Router
# ============================================================
def main() -> None:
    configure_page()

    page = st.session_state.page
    if page == "dashboard":
        dashboard()
    elif page == "add_attendance":
        add_page("➕ Add Church Attendance")
    elif page == "add_guests":
        add_page("➕ Add New Guests")
    elif page == "add_next_steps":
        add_page("➕ Add Next Steps")

# ============================================================
# Entry
# ============================================================
if __name__ == "__main__":
    main()
