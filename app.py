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
# Mock Data (replace later)
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
# Page Config + Styling
# ============================================================
def configure_page():
    st.set_page_config(
        page_title="KeepTrek Dashboard",
        layout="wide",
        page_icon="📊"
    )

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
          background: linear-gradient(180deg, #f7fbfd, #fdfefd);
          color: var(--kt-navy);
        }}

        h1, h2, h3 {{
          letter-spacing: -0.02em;
        }}

        .kt-card-title {{
          margin-bottom: 6px;
        }}

        .stButton > button {{
          background: linear-gradient(135deg, var(--kt-teal), var(--kt-green));
          color: white;
          border-radius: 8px;
          font-weight: 800;
          border: none;
          padding: 0.6rem 0.9rem;
        }}

        .stButton > button:hover {{
          background: linear-gradient(135deg, var(--kt-green), var(--kt-teal));
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# Navigation
# ============================================================
if "page" not in st.session_state:
    st.session_state.page = "dashboard"

def go(page: str):
    st.session_state.page = page
    st.rerun()

# ============================================================
# Header
# ============================================================
def render_header():
    logo = Image.open("assets/keeptrek_logo.png")

    st.image(logo, width=700)
    st.markdown(
        """
        <p style="text-align:center;
                  font-size:18px;
                  font-weight:600;
                  color:var(--kt-blue-gray);
                  margin-top:-10px;">
            Measuring Meaningful Metrics
        </p>
        """,
        unsafe_allow_html=True
    )

# ============================================================
# Trend Helpers
# ============================================================
def trend_arrow(change):
    if change == "N/A":
        return "—"
    return "↑" if change.startswith("+") else "↓"

def trend_color(change):
    if change == "N/A":
        return PALETTE["blue_gray"]
    return PALETTE["green"] if change.startswith("+") else PALETTE["navy"]

# ============================================================
# Metric Card
# ============================================================
def metric_card(title, key):
    with st.container(border=True):
        st.markdown(f"<h3 class='kt-card-title'>{title}</h3>", unsafe_allow_html=True)

        hero_value, hero_change = MOCK_DATA[key][HERO_TIME_RANGE]

        st.markdown(
            f"""
            <div style="display:flex; align-items:baseline; gap:14px;">
              <div style="font-size:54px; font-weight:900;">
                {hero_value}
              </div>
              <div style="font-size:16px; font-weight:800; color:{trend_color(hero_change)};">
                {trend_arrow(hero_change)} {hero_change}
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.divider()

        for label in TIME_RANGES[1:]:
            v, c = MOCK_DATA[key][label]
            st.markdown(
                f"""
                <div style="display:flex; justify-content:space-between;">
                  <div>{label}</div>
                  <div style="font-weight:700; color:{trend_color(c)};">
                    {v} {trend_arrow(c)} {c}
                  </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.divider()

        st.button(
            "➕ Add New Data",
            use_container_width=True,
            on_click=go,
            args=(f"add_{key}",)
        )

# ============================================================
# Dashboard Page
# ============================================================
def dashboard():
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
            <p style="color:var(--kt-blue-gray);">Coming Soon</p>
            """,
            unsafe_allow_html=True
        )

# ============================================================
# Add Pages (Blank for now)
# ============================================================
def add_page(title):
    render_header()
    st.subheader(title)
    st.info("This page will be built next.")

    st.button("⬅ Return Home", on_click=go, args=("dashboard",))

    st.markdown("### Jump to another data entry")
    col1, col2, col3 = st.columns(3)
    col1.button("Attendance", on_click=go, args=("add_attendance",))
    col2.button("Guests", on_click=go, args=("add_guests",))
    col3.button("Next Steps", on_click=go, args=("add_next_steps",))

# ============================================================
# Router
# ============================================================
def main():
    configure_page()

    if st.session_state.page == "dashboard":
        dashboard()
    elif st.session_state.page == "add_attendance":
        add_page("➕ Add Church Attendance")
    elif st.session_state.page == "add_guests":
        add_page("➕ Add New Guest")
    elif st.session_state.page == "add_next_steps":
        add_page("➕ Add Next Steps")

if __name__ == "__main__":
    main()
