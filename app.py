import streamlit as st
from PIL import Image

# =====================================
# Page Config
# =====================================
st.set_page_config(page_title="KeepTrek Dashboard", layout="wide")

# =====================================
# Logo Header
# =====================================
logo = Image.open("assets/keeptrek_logo.png")

header_col1, header_col2 = st.columns([1, 5])

with header_col1:
    st.image(logo, width=90)

with header_col2:
    st.markdown(
        """
        <h1 style="margin-bottom: 0;">KeepTrek</h1>
        <p style="color: #6b7280; margin-top: 0;">
            Turning attendance into insight
        </p>
        """,
        unsafe_allow_html=True
    )

# =====================================
# Time Range Labels
# =====================================
TIME_RANGES = [
    "Last Week",
    "Last 30 Days",
    "Last Quarter",
    "Last 90 Days",
    "One Year Snapshot",
]

# =====================================
# Mock Data (Replace later)
# Each value = (number, change_string)
# change_string examples: "+4.2%", "-1.3%", "N/A"
# =====================================
MOCK_DATA = {
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

# =====================================
# Helpers
# =====================================
def trend_arrow(change: str) -> str:
    if change == "N/A":
        return "—"
    if change.strip().startswith("-"):
        return "↓"
    if change.strip().startswith("+"):
        return "↑"
    return "→"

def trend_color(change: str) -> str:
    if change == "N/A":
        return "#6b7280"  # gray
    if change.strip().startswith("-"):
        return "#dc2626"  # red
    if change.strip().startswith("+"):
        return "#16a34a"  # green
    return "#6b7280"

def metric_card(title: str, data_key: str, key_prefix: str):
    with st.container(border=True):
        st.subheader(title)

        # Hero metric: Last Week
        value, change = MOCK_DATA[data_key]["Last Week"]
        st.markdown(
            f"""
            <div style="display:flex; align-items:baseline; gap:14px;">
              <div style="font-size:46px; font-weight:800; line-height:1;">{value}</div>
              <div style="font-size:16px; font-weight:700; color:{trend_color(change)};">
                {trend_arrow(change)} {change}
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.divider()

        # Other time ranges
        for label in TIME_RANGES[1:]:
            v, c = MOCK_DATA[data_key][label]
            st.markdown(
                f"""
                <div style="display:flex; justify-content:space-between; align-items:center; padding:4px 0;">
                  <div style="font-weight:600;">{label}</div>
                  <div style="font-weight:700; color:{trend_color(c)};">
                    {v} &nbsp; {trend_arrow(c)} {c}
                  </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.divider()

        # Actions (unique keys!)
        col_a, col_b = st.columns(2)
        with col_a:
            st.button(
                "➕ Add New Data",
                key=f"{key_prefix}_add_new_data",
                use_container_width=True
            )
        with col_b:
            st.button(
                "🔄 Refresh",
                key=f"{key_prefix}_refresh",
                use_container_width=True
            )

# =====================================
# Layout
# =====================================
col1, col2, col3 = st.columns(3)

with col1:
    metric_card("Church Attendance", "attendance", "attendance_card")

with col2:
    metric_card("New Guests", "guests", "guests_card")

with col3:
    metric_card("Next Steps", "next_steps", "next_steps_card")

st.divider()

# =====================================
# Coming Soon (non-functional)
# =====================================
with st.container(border=True):
    st.markdown(
        """
        <div style="opacity:0.65;">
          <h3 style="margin-bottom:6px;">🩺 Church Health Dashboard</h3>
          <p style="margin-top:0; color:#6b7280;">Coming Soon</p>
        </div>
        """,
        unsafe_allow_html=True
    )
