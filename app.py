import copy
import datetime
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

# =====================================
# Page Config
# =====================================
st.set_page_config(page_title="KeepTrek Dashboard", layout="wide")

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
# Each value = [number, change_string]
# change_string examples: "+4.2%", "-1.3%", "N/A"
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
    if change.strip().startswith("-"):
        return "↓"
    if change.strip().startswith("+"):
        return "↑"
    return "→"

def trend_color(change: str) -> str:
    if not isinstance(change, str) or change == "N/A":
        return "#6b7280"  # gray
    if change.strip().startswith("-"):
        return "#dc2626"  # red
    if change.strip().startswith("+"):
        return "#16a34a"  # green
    return "#6b7280"

def safe_get_metric(data: dict, key: str, label: str):
    # Returns (value:int, change:str) with sensible defaults
    try:
        entry = data.get(key, {}).get(label)
        if entry and isinstance(entry, (list, tuple)) and len(entry) >= 2:
            return int(entry[0]), str(entry[1])
    except Exception:
        pass
    return 0, "N/A"

def generate_placeholder_logo(size=(180, 60), text="KeepTrek"):
    img = Image.new("RGBA", size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    try:
        # Use a default PIL font
        font = ImageFont.load_default()
    except Exception:
        font = None
    w, h = draw.textsize(text, font=font)
    draw.text(((size[0] - w) / 2, (size[1] - h) / 2), text, fill=(40, 40, 40), font=font)
    return img

# =====================================
# Safe image load
# =====================================
def load_logo(path="assets/keeptrek_logo.png"):
    try:
        logo_img = Image.open(path)
        return logo_img
    except Exception:
        return generate_placeholder_logo()

logo = load_logo()

# =====================================
# Session state initialization
# Convert data to mutable lists if needed
# =====================================
if "data" not in st.session_state:
    st.session_state["data"] = copy.deepcopy(MOCK_DATA)
    # Ensure all metric entries are lists [value, change]
    for outer_k, v in st.session_state["data"].items():
        for label, val in v.items():
            if isinstance(val, tuple):
                st.session_state["data"][outer_k][label] = [val[0], val[1]]
            elif isinstance(val, list) and len(val) >= 2:
                # ensure types
                st.session_state["data"][outer_k][label][0] = int(st.session_state["data"][outer_k][label][0])
                st.session_state["data"][outer_k][label][1] = str(st.session_state["data"][outer_k][label][1])
            else:
                st.session_state["data"][outer_k][label] = [0, "N/A"]

if "last_refreshed" not in st.session_state:
    st.session_state["last_refreshed"] = None

# =====================================
# UI: Header + Time Range Selector
# =====================================
header_col1, header_col2 = st.columns([1, 5])

with header_col1:
    st.image(logo, width=90, use_column_width=False)

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

st.markdown("---")

selected_range = st.selectbox("Time Range", TIME_RANGES, index=0, key="selected_time_range")

# =====================================
# Metric Card renderer
# =====================================
def metric_card(title: str, data_key: str, key_prefix: str):
    # Styled card container (using markdown for border/padding)
    st.markdown(
        f"""
        <div style="
            border:1px solid #e5e7eb;
            border-radius:8px;
            padding:16px;
            background: white;
            box-shadow: 0 1px 2px rgba(0,0,0,0.02);
            ">
        """,
        unsafe_allow_html=True,
    )

    st.subheader(title)

    # Hero metric: selected_range
    value, change = safe_get_metric(st.session_state["data"], data_key, selected_range)
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

    st.markdown("<hr style='margin:12px 0;'>", unsafe_allow_html=True)

    # Other time ranges (show all ranges but highlight the selected one visually)
    for label in TIME_RANGES:
        v, c = safe_get_metric(st.session_state["data"], data_key, label)
        label_style = "font-weight:700;" if label == selected_range else "font-weight:600; color:#374151;"
        st.markdown(
            f"""
            <div style="display:flex; justify-content:space-between; align-items:center; padding:4px 0;">
              <div style="{label_style}">{label}</div>
              <div style="font-weight:700; color:{trend_color(c)};">
                {v} &nbsp; {trend_arrow(c)} {c}
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<hr style='margin:12px 0;'>", unsafe_allow_html=True)

    # Actions
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("➕ Add New Data", key=f"{key_prefix}_add_new_data"):
            # Increment value for the selected time range
            prev = st.session_state["data"].get(data_key, {}).get(selected_range, [0, "N/A"])[0]
            new_val = int(prev) + 1
            # compute a simple percent change (new vs prev). If prev==0, mark as "N/A" or "+100%"
            if prev == 0:
                percent_str = "+100%"
            else:
                percent = ((new_val - prev) / max(prev, 1)) * 100
                percent_str = f"+{round(percent,1)}%"
            st.session_state["data"][data_key][selected_range] = [new_val, percent_str]
            st.success(f"Added 1 to '{title}' ({selected_range}). Now {new_val} ({percent_str}).")
            # optional: rerun to update displayed values
            st.experimental_rerun()

    with col_b:
        if st.button("🔄 Refresh", key=f"{key_prefix}_refresh"):
            st.session_state["last_refreshed"] = datetime.datetime.utcnow().isoformat() + "Z"
            # Trigger a rerun to reflect any external changes or updated session state
            st.experimental_rerun()

    # close card div
    st.markdown("</div>", unsafe_allow_html=True)


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

st.markdown("---")

# =====================================
# Coming Soon (non-functional)
# =====================================
st.markdown(
    """
    <div style="opacity:0.85;">
      <h3 style="margin-bottom:6px;">🩺 Church Health Dashboard</h3>
      <p style="margin-top:0; color:#6b7280;">Coming Soon</p>
    </div>
    """,
    unsafe_allow_html=True
)

if st.session_state.get("last_refreshed"):
    st.caption(f"Last refreshed (UTC): {st.session_state['last_refreshed']}")
