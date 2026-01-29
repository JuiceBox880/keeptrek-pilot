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
# SIMPLE ROUTER
# ============================================================
PAGE_DASHBOARD = "dashboard"
PAGE_ATTENDANCE = "attendance_page"
PAGE_GUESTS = "guests_page"
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
# SMALL HELPER: top stats card used by all secondary pages
# ============================================================
def render_snapshot_block(key: str, title_override: str | None = None):
    data = PLACEHOLDER[key]
    title = title_override or f"{data['title']} Snapshot"

    with st.container(border=True):
        st.markdown(f"<div class='kt-card-title'>{title}</div>", unsafe_allow_html=True)
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

# ============================================================
# DASHBOARD CARD
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

        page_map = {
            "attendance": PAGE_ATTENDANCE,
            "guests": PAGE_GUESTS,
            "next_steps": PAGE_NEXT_STEPS,
        }

        col_a, col_b = st.columns(2)
        with col_a:
            st.button(
                "➕ Add New Data",
                use_container_width=True,
                key=f"{card_key}_add",
                on_click=go,
                args=(page_map[card_key],),
            )
        with col_b:
            st.button("🔄 Refresh", use_container_width=True, key=f"{card_key}_refresh")

# ============================================================
# PAGES
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

def render_attendance_page():
    render_header()
    render_snapshot_block("attendance")

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("<div class='kt-card-title'>Add Attendance</div>", unsafe_allow_html=True)
        st.caption("Placeholder page. Later we’ll add the real form + write to Sheets.")
        st.button("📝 Enter Attendance (Coming Soon)", use_container_width=True, key="att_form_placeholder")
        st.button("📷 Upload Attendance Sheet (Coming Soon)", use_container_width=True, key="att_upload_placeholder")

        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

        st.markdown("<div class='kt-ghost'>", unsafe_allow_html=True)
        st.button("⬅ Return to Dashboard", use_container_width=True, key="att_back", on_click=go, args=(PAGE_DASHBOARD,))
        st.markdown("</div>", unsafe_allow_html=True)

def render_guests_page():
    render_header()
    render_snapshot_block("guests")

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("<div class='kt-card-title'>Add New Guest</div>", unsafe_allow_html=True)
        st.caption("Placeholder page. Later we’ll add the guest form + scan card OCR.")
        st.button("🧾 Enter Guest Manually (Coming Soon)", use_container_width=True, key="guest_form_placeholder")
        st.button("📷 Upload Guest Card (Coming Soon)", use_container_width=True, key="guest_upload_placeholder")

        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

        st.markdown("<div class='kt-ghost'>", unsafe_allow_html=True)
        st.button("⬅ Return to Dashboard", use_container_width=True, key="guest_back", on_click=go, args=(PAGE_DASHBOARD,))
        st.markdown("</div>", unsafe_allow_html=True)

def render_next_steps_page():
    render_header()
    render_snapshot_block("next_steps")

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("<div class='kt-card-title'>Add Next Steps</div>", unsafe_allow_html=True)
        st.caption("Placeholder for OCR + form entry. We’ll wire this up later.")
        st.button("📷 Upload Card Here (Coming Soon)", use_container_width=True, key="ns_upload_placeholder")

        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

        st.markdown("<div class='kt-ghost'>", unsafe_allow_html=True)
        st.button("⬅ Return to Dashboard", use_container_width=True, key="ns_back", on_click=go, args=(PAGE_DASHBOARD,))
        st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# ROUTER
# ============================================================
if st.session_state.page == PAGE_DASHBOARD:
    render_dashboard()
elif st.session_state.page == PAGE_ATTENDANCE:
    render_attendance_page()
elif st.session_state.page == PAGE_GUESTS:
    render_guests_page()
elif st.session_state.page == PAGE_NEXT_STEPS:
    render_next_steps_page()
else:
    go(PAGE_DASHBOARD)
    # ============================================================
# PLANNING CENTER (stub integration - safe to add at bottom)
# ============================================================
def _pc_get_credentials():
    """
    Reads Planning Center credentials from Streamlit secrets or environment variables.
    Priority:
      1) st.secrets["PCC_APP_ID"], st.secrets["PCC_SECRET"]
      2) os.environ["PCC_APP_ID"], os.environ["PCC_SECRET"]
    """
    app_id = None
    secret = None

    # Streamlit secrets (preferred on Streamlit Cloud)
    try:
        app_id = st.secrets.get("PCC_APP_ID")
        secret = st.secrets.get("PCC_SECRET")
    except Exception:
        pass

    # Environment variables (handy locally)
    app_id = app_id or os.getenv("PCC_APP_ID")
    secret = secret or os.getenv("PCC_SECRET")

    return app_id, secret


def _pc_smoke_test():
    """
    No API calls yet. Just verifies credentials exist and are non-empty.
    """
    app_id, secret = _pc_get_credentials()
    ok = bool(app_id and secret)
    return ok, app_id, secret


def _pc_fetch_people_stub(limit: int = 10):
    """
    REAL fetch (yes, we kept the same function name to minimize changes).
    Pulls the most recently updated people (best-effort ordering).
    """
    import requests

    app_id, secret = _pc_get_credentials()
    if not (app_id and secret):
        raise RuntimeError("Missing PCC_APP_ID / PCC_SECRET")

    url = "https://api.planningcenteronline.com/people/v2/people"
    params = {
        "per_page": limit,
        # Planning Center endpoints are generally orderable; this is the common pattern.
        # If your account rejects this param, the call will still work without it.
        "order": "-updated_at",
    }

    resp = requests.get(url, auth=(app_id, secret), params=params, timeout=20)

    if resp.status_code == 401:
        raise RuntimeError("401 Unauthorized: PCC_APP_ID / PCC_SECRET are not accepted by the API.")
    if resp.status_code >= 400:
        raise RuntimeError(f"PCO error {resp.status_code}: {resp.text[:300]}")

    payload = resp.json()
    people = []

    for item in payload.get("data", []):
        attrs = item.get("attributes", {}) or {}
        first = (attrs.get("first_name") or "").strip()
        last = (attrs.get("last_name") or "").strip()
        name = (first + " " + last).strip() or attrs.get("name") or "Unknown"
        people.append(
            {
                "id": item.get("id"),
                "name": name,
                "status": "live",
                "updated_at": attrs.get("updated_at"),
                "created_at": attrs.get("created_at"),
            }
        )

    return people
