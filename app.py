import streamlit as st
from datetime import datetime

# =====================================
# Page Config
# =====================================
st.set_page_config(
    page_title="KeepTrek Dashboard",
    layout="wide"
)

# =====================================
# Header
# =====================================
st.markdown(
    """
    <h1 style='margin-bottom: 0;'>KeepTrek</h1>
    <p style='color: gray; margin-top: 0;'>Turning attendance into insight</p>
    """,
    unsafe_allow_html=True
)

st.divider()

# =====================================
# Time Range Labels
# =====================================
TIME_RANGES = [
    "Last Week",
    "Last 30 Days",
    "Last Quarter",
    "Last 90 Days",
    "One Year Snapshot"
]

# =====================================
# Mock Data (REPLACE LATER)
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
    }
}

# =====================================
# Helper UI Functions
# =====================================
def trend_arrow(change):
    if change == "N/A":
        return "—"
    if change.startswith("-"):
        return "↓"
    return "↑"

def metric_card(title, data_key):
    with st.container(border=True):
        st.subheader(title)

        # --- Hero Metric ---
        value, change = MOCK_DATA[data_key]["Last Week"]
        st.markdown(
            f"""
            <h1 style='margin-bottom: 0;'>{value}</h1>
            <p style='color: {"green" if "+" in change else "red" if "-" in change else "gray"};'>
                {trend_arrow(change)} {change}
            </p>
            """,
            unsafe_allow_html=True
        )

        st.divider()

        # --- Other Time Ranges ---
        for label in TIME_RANGES[1:]:
            v, c = MOCK_DATA[data_key][label]
            st.write(
                f"**{label}:** {v}  {trend_arrow(c)} {c}"
            )

        st.divider()

        # --- Actions ---
        col_a, col_b = st.columns(2)
        with col_a:
            st.button("➕ Add New Data", use_container_width=True)
        with col_b:
            st.button("🔄 Refresh", use_container_width=True)

# =====================================
# Main Dashboard Layout
# =====================================
col1, col2, col3 = st.columns(3)

with col1:
    metric_card("Church Attendance", "attendance")

with col2:
    metric_card("New Guests", "guests")

with col3:
    metric_card("Next Steps", "next_steps")

st.divider()

# =====================================
# Coming Soon Section
# =====================================
with st.container(border=True):
    st.markdown(
        """
        <h3 style='color: gray;'>🩺 Church Health Dashboard</h3>
        <p style='color: gray;'>Coming Soon</p>
        """,
        unsafe_allow_html=True
    )
