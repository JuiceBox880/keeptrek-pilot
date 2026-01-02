import streamlit as st
from PIL import Image
import os

# ============================================================
# THEME (KeepTrek)
# ============================================================
PALETTE = {
    "navy": "#054063",
    "teal": "#179171",
    "green": "#34a94d",
    "blue_gray": "#47919e",
    "muted": "#6b7280",
    "bg_top": "#f7fbfd",
    "bg_bottom": "#fdfefe",
}

TIME_RANGES = ["Last Week", "Last 30 Days", "Last Quarter", "Last 90 Days", "One Year Snapshot"]

# ============================================================
# PLACEHOLDER DATA (hard-coded)
# ============================================================
PLACEHOLDER = {
    "attendance": {
        "title": "Church Attendance",
        "caption": "Total attendance (all services)",
        "hero": 248,
        "ranges": {
            "Last 30 Days": 982,
            "Last Quarter": 2901,
            "Last 90 Days": 2875,
            "One Year Snapshot": 11234,
        },
        "trend": "+4.2%",
    },
    "guests": {
        "title": "New Guests",
        "caption": "Total new guests",
        "hero": 21,
        "ranges": {
            "Last 30 Days": 78,
            "Last Quarter": 212,
            "Last 90 Days": 201,
            "One Year Snapshot": 865,
        },
        "trend": "+10%",
    },
    "next_steps": {
        "title": "Next Steps",
        "caption": "People taking next steps",
        "hero": 14,
        "ranges": {
            "Last 30 Days": 63,
            "Last Quarter": 188,
            "Last 90 Days": 179,
            "One Year Snapshot": 742,
        },
        "trend": "+5%",
    },
}

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(page_title="KeepTrek Dashboard (Placeholder)", layout="wide", page_icon="📊")

# ============================================================
# SIMPLE ROUTER (Dashboard -> Next Steps page)
# ============================================================
PAGE_DASHBOARD = "dashboard"
PAGE_NEXT_STEPS = "next_steps_page"

if "page" not in st.session_state:
    st.session_state.page = PAGE_DASHBOARD

def go(page: str) -> None:
    st.session_state.page = page
    st.rerun()

# ============================================================
# STYLING
# ============================================================
st.markdown(
    f"""
    <style>
      :root {{
        --kt-navy: {PALETTE['navy']};
        --kt-teal: {PALETTE['teal']};
        --kt-green: {PALETTE['green']};
        --kt-blue-gray: {PALETTE['blue_gray']};
        --kt-muted: {PALETTE['muted']};
        --kt-bg-top: {PALETTE['bg_top']};
        --kt-bg-bottom: {PALETTE['bg_bottom']};
      }}

      html, body, [data-testid="stAppViewContainer"] {{
        background: linear-gradient(180deg, var(--kt-bg-top) 0%, var(--kt-bg-bottom) 100%) !important;
      }}

      .block-container {{
        padding-top: 1.4rem;
        padding-bottom: 2.2rem;
        max-width: 1200px;
      }}

      h1, h2, h3, h4 {{
        color: var(--kt-navy);
        letter-spacing: -0.02em;
      }}

      .kt-tagline {{
        color: var(--kt-blue-gray);
        font-weight: 700;
        text-align: center;
        margin-top: 0.35rem;
        margin-bottom: 0.2rem;
      }}

      .kt-card-title {{
        margin: 0 0 0.35rem 0;
        font-size: 1.25rem;
        font-weight: 900;
        color: var(--kt-navy);
      }}

      .kt-hero-number {{
        font-size: 3.2rem;
        font-weight: 950;
        line-height: 1;
        color: var(--kt-navy);
      }}

      .kt-hero-sub {{
        font-size: 0.95rem;
        font-weight: 650;
        color: var(--kt-blue-gray);
        margin-top: 0.25rem;
      }}

      .kt-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.35rem 0;
        border-bottom: 1px solid rgba(5, 64, 99, 0.08);
      }}

      .kt-row:last-child {{
        border-bottom: none;
      }}

      .kt-row-label {{
        font-weight: 750;
        color: var(--kt-navy);
      }}

      .kt-row-value {{
        font-weight: 900;
        color: var(--kt-navy);
      }}

      .kt-chip {{
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.25rem 0.55rem;
        border-radius: 999px;
        font-weight: 850;
        font-size: 0.85rem;
        background: rgba(23, 145, 113, 0.12);
        color: var(--kt-teal);
      }}

      div[data-testid="stVerticalBlockBorderWrapper"] {{
        border-radius: 14px !important;
        border: 1px solid rgba(5, 64, 99, 0.10) !important;
        box-shadow: 0 8px 24px rgba(5, 64, 99, 0.06) !important;
        background: rgba(255, 255, 255, 0.92) !important;
      }}

      .stButton > button {{
        background: linear-gradient(135deg, var(--kt-teal), var(--kt-green)) !important;
        color: white !important;
        font-weight: 900 !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 0.70rem 0.95rem !important;
        box-shadow: 0 10px 20px rgba(5, 64, 99, 0.14) !important;
      }}

      .stButton > button:hover {{
        background: linear-gradient(135deg, var(--kt-green), var(--kt-teal)) !important;
        box-shadow: 0 14px 28px rgba(5, 64, 99, 0.16) !important;
      }}

      .stButton > button:focus {{
        outline: 2px solid var(--kt-blue-gray) !important;
      }}

      /* "Ghost" button wrapper */
      .kt-ghost .stButton > button {{
        background: transparent !important;
        color: var(--kt-navy) !important;
        border: 1px solid rgba(5, 64, 99, 0.20) !important;
        box-shadow: none !important;
      }}

      .kt-ghost .stButton > button:hover {{
        background: rgba(71, 145, 158, 0.08) !important;
      }}

      .kt-footer {{
        text-align: center;
        color: var(--kt-muted);
        font-weight: 700;
        margin-top: 0.75rem;
      }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# LOGO (safe load)
# ============================================================
def load_logo():
    path = os.path.join("assets", "keeptrek_logo.png")
    if os.path.exists(path):
        return Image.open(path)
    return None

def render_header():
    logo = load_logo()
    spacer, center, spacer2 = st.columns([1, 2, 1])
    with center:
        if logo:
            st.image(logo, width=720)
        else:
            st.markdown("<h1 style='text-align:center; margin-bottom:0;'>KeepTrek</h1>", unsafe_allow_html=True)
        st.markdown("<div class='kt-tagline'>Measuring Meaningful Metrics</div>", unsafe_allow_html=True)
    st.divider()

# ============================================================
# UI COMPONENTS
# ============================================================
def metric_card(card_key: str):
    data = PLACEHOLDER[card_key]

    with st.container(border=True):
        st.markdown(f"<div class='kt-card-title'>{data['title']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='kt-hero-number'>{data['hero']}</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='kt-hero-sub'>{data['caption']} &nbsp; • &nbsp; "
            f"<span class='kt-chip'>↑ {data['trend']}</span></div>",
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

        for label in TIME_RANGES[1:]:
            val = data["ranges"].get(label, "—")
            st.markdown(
                f"""
                <div class="kt-row">
                  <div class="kt-row-label">{label}</div>
                  <div class="kt-row-value">{val}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            if card_key == "next_steps":
                st.button(
                    "➕ Add New Data",
                    use_container_width=True,
                    key=f"{card_key}_add",
                    on_click=go,
                    args=(PAGE_NEXT_STEPS,),
                )
            else:
                st.button("➕ Add New Data", use_container_width=True, key=f"{card_key}_add")

        with col_b:
            st.button("🔄 Refresh", use_container_width=True, key=f"{card_key}_refresh")

def render_next_steps_page():
    render_header()

    # Top stats (same data as dashboard)
    with st.container(border=True):
        st.markdown("<div class='kt-card-title'>Next Steps Snapshot</div>", unsafe_allow_html=True)

        data = PLACEHOLDER["next_steps"]
        st.markdown(f"<div class='kt-hero-number'>{data['hero']}</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='kt-hero-sub'>{data['caption']} &nbsp; • &nbsp; "
            f"<span class='kt-chip'>↑ {data['trend']}</span></div>",
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
        for label in TIME_RANGES[1:]:
            val = data["ranges"].get(label, "—")
            st.markdown(
                f"""
                <div class="kt-row">
                  <div class="kt-row-label">{label}</div>
                  <div class="kt-row-value">{val}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    # Upload Card (non-functional placeholder)
    with st.container(border=True):
        st.markdown("<div class='kt-card-title'>Add Next Steps</div>", unsafe_allow_html=True)
        st.caption("Placeholder for OCR + form entry. We’ll wire this up later.")
        st.button("📷 Upload Card Here (Coming Soon)", use_container_width=True, key="ns_upload_placeholder")

        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

        # Home button
        st.markdown("<div class='kt-ghost'>", unsafe_allow_html=True)
        st.button("⬅ Return to Dashboard", use_container_width=True, key="ns_back", on_click=go, args=(PAGE_DASHBOARD,))
        st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# ROUTED PAGES
# ============================================================
def render_dashboard():
    render_header()

    col1, col2, col3 = st.columns(3)
    with col1:
        metric_card("attendance")
    with col2:
        metric_card("guests")
    with col3:
        metric_card("next_steps")

    st.divider()

    with st.container(border=True):
        st.markdown(
            """
            <div style="opacity:0.78;">
              <h3 style="margin-bottom:6px; color: var(--kt-navy);">🩺 Church Health Dashboard</h3>
              <p style="margin-top:0; color: var(--kt-blue-gray); font-weight:700;">Coming Soon</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div class='kt-footer'>KeepTrek • Church Metrics Made Meaningful</div>", unsafe_allow_html=True)

# ============================================================
# MAIN
# ============================================================
if st.session_state.page == PAGE_DASHBOARD:
    render_dashboard()
elif st.session_state.page == PAGE_NEXT_STEPS:
    render_next_steps_page()
else:
    # fallback
    go(PAGE_DASHBOARD)
