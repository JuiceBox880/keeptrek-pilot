from typing import Dict, Tuple

import pandas as pd
import streamlit as st
from PIL import Image
import gspread
from google.oauth2.service_account import Credentials

# ============================================================
# CONFIG
# ============================================================
SHEET_NAME = "KeepTrek_Data"
TAB_ATTENDANCE = "Attendance"
TAB_GUESTS = "New_Guests"
TAB_NEXT_STEPS = "Next_Steps"

# ============================================================
# TYPES
# ============================================================
MetricValue = Tuple[int, str]

# ============================================================
# NAVIGATION
# ============================================================
PAGE_DASHBOARD = "dashboard"
PAGE_ADD_ATTENDANCE = "add_attendance"
PAGE_ADD_GUESTS = "add_guests"
PAGE_ADD_NEXT_STEPS = "add_next_steps"

if "page" not in st.session_state:
    st.session_state.page = PAGE_DASHBOARD


def go(page: str) -> None:
    st.session_state.page = page
    st.rerun()


# ============================================================
# PAGE SETUP + STYLING
# ============================================================
st.set_page_config(page_title="KeepTrek Dashboard", layout="wide", page_icon="📊")

st.markdown(
    """
    <style>
    body {
        background: linear-gradient(180deg, #f7fbfd, #fdfefe);
    }
    h1, h2, h3 {
        color: #054063;
    }
    .stButton>button {
        background: linear-gradient(135deg, #179171, #34a94d);
        color: white;
        font-weight: 800;
        border-radius: 8px;
        border: none;
        padding: 0.6rem 0.9rem;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #34a94d, #179171);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# GOOGLE SHEETS CONNECTION
# ============================================================
def _credentials() -> Credentials:
    return Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )


@st.cache_resource
def get_gsheet() -> gspread.Spreadsheet:
    client = gspread.authorize(_credentials())
    return client.open(SHEET_NAME)


sheet = get_gsheet()


def load_tab(tab_name: str) -> pd.DataFrame:
    try:
        worksheet = sheet.worksheet(tab_name)
        data = worksheet.get_all_records()
        return pd.DataFrame(data)
    except Exception:
        return pd.DataFrame()


attendance_df = load_tab(TAB_ATTENDANCE)
guests_df = load_tab(TAB_GUESTS)
next_steps_df = load_tab(TAB_NEXT_STEPS)

# ============================================================
# METRIC CALCULATIONS
# ============================================================
def safe_sum(df: pd.DataFrame, col: str) -> int:
    return int(df[col].sum()) if col in df.columns else 0


attendance_total = safe_sum(attendance_df, "Attendance Count")
new_guest_total = len(guests_df)
next_steps_total = len(next_steps_df)

# ============================================================
# HEADER
# ============================================================
logo = Image.open("assets/keeptrek_logo.png")

spacer, center, spacer2 = st.columns([1, 2, 1])
with center:
    st.image(logo, width=720)
    st.markdown(
        "<p style='text-align:center;color:#47919e;font-weight:700;'>"
        "Measuring Meaningful Metrics</p>",
        unsafe_allow_html=True,
    )

# ============================================================
# DASHBOARD CARDS
# ============================================================
def dashboard_card(title: str, value: int, caption: str, add_page: str) -> None:
    with st.container(border=True):
        st.subheader(title)
        st.markdown(f"<h1>{value}</h1>", unsafe_allow_html=True)
        st.caption(caption)
        st.button(
            "➕ Add New Data",
            use_container_width=True,
            on_click=go,
            args=(add_page,),
        )


col1, col2, col3 = st.columns(3)

with col1:
    dashboard_card(
        "Church Attendance",
        attendance_total,
        "Total attendance (all services)",
        PAGE_ADD_ATTENDANCE,
    )

with col2:
    dashboard_card(
        "New Guests",
        new_guest_total,
        "Total new guests",
        PAGE_ADD_GUESTS,
    )

with col3:
    dashboard_card(
        "Next Steps",
        next_steps_total,
        "People taking next steps",
        PAGE_ADD_NEXT_STEPS,
    )

st.divider()

# ============================================================
# FORMS
# ============================================================
def append_row(tab_name: str, row: Dict[str, str]) -> None:
    try:
        worksheet = sheet.worksheet(tab_name)
        worksheet.append_row(list(row.values()))
        st.success("Saved!")
        st.rerun()
    except Exception as exc:
        st.error(f"Unable to save data: {exc}")


def add_attendance() -> None:
    st.subheader("➕ Add Church Attendance")
    with st.form("attendance_form"):
        date = st.date_input("Service Date")
        count = st.number_input("Attendance Count", min_value=0, step=1)
        submitted = st.form_submit_button("Save Attendance")
        if submitted:
            append_row(
                TAB_ATTENDANCE,
                {
                    "Service Date": str(date),
                    "Attendance Count": int(count),
                },
            )


def add_guest() -> None:
    st.subheader("➕ Add New Guest")
    with st.form("guest_form"):
        name = st.text_input("Guest Name")
        visit_date = st.date_input("Visit Date")
        contact = st.text_input("Contact Info (optional)")
        submitted = st.form_submit_button("Save Guest")
        if submitted:
            append_row(
                TAB_GUESTS,
                {
                    "Guest Name": name,
                    "Visit Date": str(visit_date),
                    "Contact Info": contact,
                },
            )


def add_next_step() -> None:
    st.subheader("➕ Add Next Step")
    with st.form("next_steps_form"):
        name = st.text_input("Name")
        step = st.text_input("Next Step")
        date = st.date_input("Date")
        submitted = st.form_submit_button("Save Next Step")
        if submitted:
            append_row(
                TAB_NEXT_STEPS,
                {
                    "Name": name,
                    "Next Step": step,
                    "Date": str(date),
                },
            )

# ============================================================
# DATA PREVIEWS
# ============================================================
def render_previews() -> None:
    with st.container(border=True):
        st.subheader("📊 Attendance Records")
        if attendance_df.empty:
            st.info("No attendance data yet.")
        else:
            st.dataframe(attendance_df, use_container_width=True)

    with st.container(border=True):
        st.subheader("👋 New Guests")
        if guests_df.empty:
            st.info("No guest data yet.")
        else:
            st.dataframe(guests_df, use_container_width=True)

    with st.container(border=True):
        st.subheader("➡️ Next Steps")
        if next_steps_df.empty:
            st.info("No next steps data yet.")
        else:
            st.dataframe(next_steps_df, use_container_width=True)

# ============================================================
# ROUTER
# ============================================================
def render_nav_buttons() -> None:
    st.markdown("### Jump to another data entry")
    col1, col2, col3 = st.columns(3)
    col1.button("Attendance", on_click=go, args=(PAGE_ADD_ATTENDANCE,))
    col2.button("Guests", on_click=go, args=(PAGE_ADD_GUESTS,))
    col3.button("Next Steps", on_click=go, args=(PAGE_ADD_NEXT_STEPS,))


def render_body() -> None:
    if st.session_state.page == PAGE_DASHBOARD:
        render_previews()
    elif st.session_state.page == PAGE_ADD_ATTENDANCE:
        add_attendance()
        render_nav_buttons()
    elif st.session_state.page == PAGE_ADD_GUESTS:
        add_guest()
        render_nav_buttons()
    elif st.session_state.page == PAGE_ADD_NEXT_STEPS:
        add_next_step()
        render_nav_buttons()


def render_footer() -> None:
    st.markdown(
        "<p style='text-align:center;color:#6b7280;font-weight:600;'>"
        "KeepTrek • Church Metrics Made Meaningful</p>",
        unsafe_allow_html=True,
    )


render_body()
render_footer()
