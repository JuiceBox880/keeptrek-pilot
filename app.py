import copy
import os
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

# ============================================================
# KeepTrek (Pilot) — Dashboard + Placeholder Pages
# Clean, stable, no “time range selector” (everything visible)
# ============================================================

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="KeepTrek Dashboard", layout="wide")

# -----------------------------
# Router (simple + reliable)
# -----------------------------
if "page" not in st.session_state:
    st.session_state["page"] = "dashboard"

def go_to(page_name: str):
    st.session_state["page"] = page_name
    st.rerun()

# -----------------------------
# Data Labels (always shown)
# -----------------------------
TIME_RANGES = [
    "Last Week",
    "Last 30 Days",
    "Last Quarter",
    "Last 90 Days",
    "One Year Snapshot",
]

# -----------------------------
# Mock Data (swap later for Sheets)
# Each entry: [value, change_string]
# change_string: "+4.2%", "-1.3%", or "N/A"
# -----------------------------
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

# -----------------------------
# Session State Init
# -----------------------------
if "data" not in st.session_state:
    st.session_state["data"] = copy.deepcopy(MOCK_DATA)

# -----------------------------
# Helpers
# -----------------------------
def trend_arrow(change: str) -> str:
    if not isinstance(change, str) or change == "N/A":
        return "—"
    s = change.strip()
    if s.startswith("-"):
        return "↓"
    if s.startswith("+"):
        return "↑"
    return "→"

def trend_color(change: str) -> str:
    if not isinstance(change, str) or change == "N/A":
        return "#6b7280"  # gray
    s = change.strip()
    if s.startswith("-"):
        return "#dc2626"  # red
    if s.startswith("+"):
        return "#16a34a"  # green
    return "#6b7280"

def safe_get_metric(data: dict, key: str, label: str):
    try:
        entry = data.get(key, {}).get(label)
        if entry and isinstance(entry, (list, tuple)) and len(entry) >= 2:
            return int(entry[0]), str(entry[1])
    except Exception:
        pass
    return 0, "N/A"

def generate_placeholder_logo(size=(220, 70), text="KeepTrek"):
    img = Image.new("RGBA", size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None
    # NOTE: draw.textbbox not always available on older PIL; keep simple
    w, h = draw.textsize(text, font=font)
    draw.text(((size[0] - w) / 2, (size[1] - h) / 2), text, fill=(40, 40, 40), font=font)
    return img

def load_logo():
    try:
        base = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(base, "assets", "keeptrek_logo.png")
        return Image.open(logo_path)
    except Exception:
        return generate_placeholder_logo()

logo = load_logo()

# -----------------------------
# Global Style (subtle polish)
# -----------------------------
st.markdown(
    """
    <style>
      /* Tighten top padding a bit */
      .block-container { padding-top: 1.4rem; padding-bottom: 2.2rem; }

      /* Make headings feel a bit more “product” */
      h1, h2, h3 { letter-spacing: -0.02em; }

      /* Improve card spacing on smaller screens */
      @media (max-width: 900px) {
        .block-container { padding-left: 1rem; padding-right: 1rem; }
      }
    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# Header (all pages)
# ============================================================
header_col1, header_col2 = st.columns([2, 7], vertical_alignment="center")

with header_col1:
    st.image(logo, width=190)

with header_col2:
    st.markdown(
        """
        <div style="line-height: 1.1;">
          <div style="font-size: 44px; font-weight: 850; margin: 0;">KeepTrek</div>
          <div style="color:#6b7280; font-size: 16px; margin-top: 6px;">
            Turning attendance into insight
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.divider()

# ============================================================
# Dashboard Page
# ============================================================
if st.session_state["page"] == "dashboard":

    def metric_card(title: str, data_key: str, key_prefix: str):
        with st.container(border=True):
            st.subheader(title)

            # --- Hero metric: Last Week (largest, always)
            hero_value, hero_change = safe_get_metric(st.session_state["data"], data_key, "Last Week")
            st.markdown(
                f"""
                <div style="display:flex; align-items:baseline; gap:14px; margin-top:4px;">
                  <div style="font-size:52px; font-weight:900; line-height:1;">{hero_value}</div>
                  <div style="font-size:16px; font-weight:750; color:{trend_color(hero_change)};">
                    {trend_arrow(hero_change)} {hero_change}
                  </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

            # --- Snapshot list (everything visible, clean)
            for label in TIME_RANGES[1:]:
                v, c = safe_get_metric(st.session_state["data"], data_key, label)
                st.markdown(
                    f"""
                    <div style="display:flex; justify-content:space-between; align-items:center; padding:4px 0;">
                      <div style="font-weight:650; color:#374151;">{label}</div>
                      <div style="font-weight:750; color:{trend_color(c)};">
                        {v} &nbsp; {trend_arrow(c)} {c}
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.divider()

            # --- Actions (wired to routing; refresh is placeholder)
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("➕ Add New Data", key=f"{key_prefix}_add", use_container_width=True):
                    go_to(f"add_{data_key}")
            with col_b:
                st.button("🔄 Refresh", key=f"{key_prefix}_refresh", use_container_width=True)

    # --- 3-card layout
    col1, col2, col3 = st.columns(3)
    with col1:
        metric_card("Church Attendance", "attendance", "attendance")
    with col2:
        metric_card("New Guests", "guests", "guests")
    with col3:
        metric_card("Next Steps", "next_steps", "next_steps")

    st.divider()

    # --- Coming Soon (non-functional)
    with st.container(border=True):
        st.markdown(
            """
            <div style="opacity:0.8;">
              <div style="font-size:20px; font-weight:800;">🩺 Church Health Dashboard</div>
              <div style="color:#6b7280; margin-top:6px;">Coming Soon</div>
            </div>
            """,
            unsafe_allow_html=True
        )

# ============================================================
# Placeholder Pages
# ============================================================
elif st.session_state["page"] == "add_attendance":
    st.subheader("➕ Add Church Attendance")
    st.write("Blank page for now. We’ll build the form here next.")
    st.button("⬅ Back to Dashboard", on_click=go_to, args=("dashboard",), use_container_width=False)

elif st.session_state["page"] == "add_guests":
    st.subheader("➕ Add New Guest")
    st.write("Blank page for now. We’ll build manual entry + scan card here.")
    st.button("⬅ Back to Dashboard", on_click=go_to, args=("dashboard",), use_container_width=False)

elif st.session_state["page"] == "add_next_steps":
    st.subheader("➕ Add Next Steps")
    st.write("Blank page for now. We’ll build checkboxes + entry here.")
    st.button("⬅ Back to Dashboard", on_click=go_to, args=("dashboard",), use_container_width=False)

else:
    # Safety fallback
    st.session_state["page"] = "dashboard"
    st.rerun()
