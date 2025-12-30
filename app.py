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
# Navigation
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
    st.set_page_config(
        page_title="KeepTrek Dashboard",
        layout="wide",
        page_icon="📊",
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
          background: linear-gradient(180deg, #f7fbfd 0%, #f4f8fa 45%, #fdfefd 100%);
          color: var(--kt-navy);
        }}

        h1, h2, h3, h4 {{
          color: var(--kt-navy);
        }}

        .kt-card-title {{
          margin-bottom: 6px;
        }}

        .stButton > button {{
          background: linear-gradient(135deg, var(--kt-teal), var(--kt-green));
          color: white;
          border: none;
          border-radius: 8px;
          font-weight: 800;
          padding: 0.65rem 0.95rem;
          box-shadow: 0 2px 8px rgba(5, 64, 99, 0.18);
        }}

        .stButton > button:hover {{
          background: linear-gradient(135deg, var(--kt-green), var(--kt-teal));
          box-shadow: 0 6px 14px rgba(5, 64, 99, 0.18);
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
            <p style="
                color: var(--kt-blue-gray);
                margin-top: 6px;
                font-weight: 700;
                text-align: center;
            ">
                Measuring Meaningful Metrics
            </p>
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
# Metric Card Rendering
# ============================================================
def render_metric_row(label: str, value: int, change: str) -> None:
    st.markdown(
        f"""
        <div style="display:flex; justify-content:space-between; padding:4px 0;">
          <div style="font-weight:600;">{label}</div>
          <div style="font-weight:700; color:{trend_color(change)};">
            {value} {trend_arrow(change)} {change}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_hero_metric(value: int, change: str) -> None:
    st.markdown(
        f"""
        <div style="display:flex; align-items:baseline; gap:14px;">
          <div style="font-size:54px; font-weight:900;">{value}</div>
          <div style="font-size:16px; font-weight:900; color:{trend_color(change)};">
            {trend_arrow(change)} {change}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(title: str, data_key: str) -> None:
    with st.container(border=True):
        st.markdown(f"<h3 class='kt-card-title'>{title}</h3>", unsafe_allow_html=True)

        value, change = MOCK_DATA[data_key][HERO_TIME_RANGE]
        render_hero_metric(value, change)

        st.divider()

        for label in TIME_RANGES[1:]:
            v, c = MOCK_DATA[data_key][label]
            render_metric_row(label, v, c)

        st.divider()

        if st.button("➕ Add New Data", use_container_width=True):
            go(f"add_{data_key}")


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
            <p style="color: var(--kt-blue-gray); font-weight:600;">
                Coming Soon
            </p>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# Add Pages
# ============================================================
ADD_PAGE_FIELDS = {
    "attendance": [
        ("Service date", "date"),
        ("Total attendance", "number"),
        ("Adults", "number"),
        ("Students", "number"),
        ("Notes", "text"),
    ],
    "guests": [
        ("Visit date", "date"),
        ("New guest count", "number"),
        ("Follow-up scheduled?", "checkbox"),
        ("Notes", "text"),
    ],
    "next_steps": [
        ("Date", "date"),
        ("Commitments", "number"),
        ("Baptisms", "number"),
        ("First-time decisions", "number"),
        ("Notes", "text"),
    ],
}


def add_page(title: str, key: str) -> None:
    render_header()
    st.subheader(title)

    with st.form(f"{key}_form"):
        for label, field_type in ADD_PAGE_FIELDS[key]:
            if field_type == "date":
                st.date_input(label)
            elif field_type == "number":
                st.number_input(label, min_value=0, step=1)
            elif field_type == "checkbox":
                st.checkbox(label)
            else:
                st.text_area(label)

        submitted = st.form_submit_button("Save Entry", use_container_width=True)

    if submitted:
        st.success("Entry saved (mock).")

    st.divider()
    st.button("⬅ Return Home", use_container_width=True, on_click=go, args=("dashboard",))


# ============================================================
# Router
# ============================================================
def main() -> None:
    configure_page()

    page = st.session_state.page
    if page == "dashboard":
        dashboard()
    elif page == "add_attendance":
        add_page("➕ Add Church Attendance", "attendance")
    elif page == "add_guests":
        add_page("➕ Add New Guest", "guests")
    elif page == "add_next_steps":
        add_page("➕ Add Next Steps", "next_steps")


if __name__ == "__main__":
    main()
