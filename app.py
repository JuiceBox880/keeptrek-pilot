import copy
import datetime
import os
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

# =====================================
# Page Config
# =====================================
st.set_page_config(page_title="KeepTrek Dashboard", layout="wide")

# =====================================
# Simple Page Router
# =====================================
if "page" not in st.session_state:
    st.session_state["page"] = "dashboard"

def go_to(page_name: str):
    st.session_state["page"] = page_name
    st.experimental_rerun()

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
# =====================================
MOCK_DATA = {
    "attendance": {
        "Last Week": [248, "+4.2%"],
        "Last 30 Days": [982, "+1.1%"],
        "Last Quarter": [2901, "-0.6%"],
        "Last 90 Days": [2875, "N/A"],
        "One Year Snapshot": [11234, "+6.4%"],
    },
    "guests": {
        "Last Week": [21, "+10%"],
        "Last 30 Days": [78, "+3%"],
        "Last Quarter": [212, "-2%"],
        "Last 90 Days": [201, "N/A"],
        "One Year Snapshot": [865, "+8%"],
    },
    "next_steps": {
        "Last Week": [14, "+5%"],
        "Last 30 Days": [63, "+2%"],
        "Last Quarter": [188, "+1%"],
        "Last 90 Days": [179, "N/A"],
        "One Year Snapshot": [742, "+4%"],
    },
}

# =====================================
# Helpers
# =====================================
def trend_arrow(change: str) -> str:
    if not isinstance(change, str) or change == "N/A":
        return "—"
    if change.startswith("-"):
        return "↓"
    if change.startswith("+"):
        return "↑"
    return "→"

def trend_color(change: str) -> str:
    if not isinstance(change, str) or change == "N/A":
        return "#6b7280"
    if change.startswith("-"):
        return "#dc2626"
    if change.startswith("+"):
        return "#16a34a"
    return "#6b7280"

def safe_get_metric(data: dict, key: str, label: str):
    try:
        entry = data.get(key, {}).get(label)
        if entry and len(entry) >= 2:
            return int(entry[0]), str(entry[1])
    except Exception:
        pass
    return 0, "N/A"

def generate_placeholder_logo(size=(180, 60), text="KeepTrek"):
    img = Image.new("RGBA", size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    w, h = draw.textsize(text, font=font)
    draw.text(((size[0]-w)/2, (size[1]-h)/2), text, fill=(40,40,40), font=font)
    return img

def load_logo():
    try:
        base = os.path.dirname(os.path.abspath(__file__))
        return Image.open(os.path.join(base, "assets", "keeptrek_logo.png"))
    except Exception:
        return generate_placeholder_logo()

logo = load_logo()

# =====================================
# Session State Init
# =====================================
if "data" not in st.session_state:
    st.session_state["data"] = copy.deepcopy(MOCK_DATA)

# =====================================
# Header (all pages)
# =====================================
header_col1, header_col2 = st.columns([2, 6])
with header_col1:
    st.image(logo, width=160)
with header_col2:
    st.markdown(
        """
        <h1 style="margin-bottom:0;">KeepTrek</h1>
        <p style="color:#6b7280;margin-top:0;">Turning attendance into insight</p>
        """,
        unsafe_allow_html=True
    )

st.divider()

# =====================================
# DASHBOARD PAGE
# =====================================
if st.session_state["page"] == "dashboard":

    selected_range = st.selectbox("Time Range", TIME_RANGES, index=0)

    def metric_card(title: str, data_key: str, key_prefix: str):
        st.markdown(
            """
            <div style="
                border:1px solid #e5e7eb;
                border-radius:8px;
                padding:16px;
                background:white;">
            """,
            unsafe_allow_html=True
        )

        st.subheader(title)

        value, change = safe_get_metric(st.session_state["data"], data_key, selected_range)
        st.markdown(
            f"""
            <div style="display:flex;align-items:baseline;gap:14px;">
              <div style="font-size:46px;font-weight:800;">{value}</div>
              <div style="font-weight:700;color:{trend_color(change)};">
                {trend_arrow(change)} {change}
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<hr>", unsafe_allow_html=True)

        for label in TIME_RANGES:
            v, c = safe_get_metric(st.session_state["data"], data_key, label)
            st.markdown(
                f"""
                <div style="display:flex;justify-content:space-between;">
                  <div>{label}</div>
                  <div style="color:{trend_color(c)};">
                    {v} {trend_arrow(c)} {c}
                  </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("<hr>", unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("➕ Add New Data", key=f"{key_prefix}_add"):
                go_to(f"add_{data_key}")
        with col_b:
            st.button("🔄 Refresh", key=f"{key_prefix}_refresh")

        st.markdown("</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        metric_card("Church Attendance", "attendance", "attendance")
    with col2:
        metric_card("New Guests", "guests", "guests")
    with col3:
        metric_card("Next Steps", "next_steps", "next_steps")

    st.divider()

    st.markdown(
        """
        <div style="opacity:.7;">
          <h3>🩺 Church Health Dashboard</h3>
          <p>Coming Soon</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# =====================================
# ADD PAGES (PLACEHOLDERS)
# =====================================
elif st.session_state["page"] == "add_attendance":
    st.subheader("➕ Add Church Attendance")
    st.write("This page will contain the attendance form.")
    st.button("⬅ Back to Dashboard", on_click=go_to, args=("dashboard",))

elif st.session_state["page"] == "add_guests":
    st.subheader("➕ Add New Guest")
    st.write("This page will contain guest entry and scan card.")
    st.button("⬅ Back to Dashboard", on_click=go_to, args=("dashboard",))

elif st.session_state["page"] == "add_next_steps":
    st.subheader("➕ Add Next Steps")
    st.write("This page will contain next steps selection.")
    st.button("⬅ Back to Dashboard", on_click=go_to, args=("dashboard",))
