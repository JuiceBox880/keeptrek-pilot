import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# =========================
# GOOGLE AUTH HELPERS
# =========================

SHEETS_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def get_sheets_credentials() -> Credentials:
    if "gcp_service_account_sheets" not in st.secrets:
        st.error("Missing secret: gcp_service_account_sheets")
        st.stop()

    sa_info = dict(st.secrets["gcp_service_account_sheets"])
    return Credentials.from_service_account_info(
        sa_info,
        scopes=SHEETS_SCOPES
    )

def get_vision_credentials() -> Credentials:
    if "gcp_service_account_vision" not in st.secrets:
        st.error("Missing secret: gcp_service_account_vision")
        st.stop()

    sa_info = dict(st.secrets["gcp_service_account_vision"])
    return Credentials.from_service_account_info(sa_info)

def get_sheet():
    client = gspread.authorize(get_sheets_credentials())
    return client.open("KeepTrek_Data")

# ---------------------------------------------------------------------------
# Configuration and constants
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SheetsConfig:
    """Configuration for Google Sheet and worksheet names."""
    sheet_name: str = "KeepTrek_Data"
    attendance_tab: str = "Attendance"
    guests_tab: str = "New_Guests"
    next_steps_tab: str = "Next_Steps"

CONFIG = SheetsConfig()

# Page identifiers for navigation
PAGE_DASHBOARD = "dashboard"
PAGE_ADD_ATTENDANCE = "add_attendance"
PAGE_ADD_GUESTS = "add_guests"
PAGE_ADD_NEXT_STEPS = "add_next_steps"

# ---------------------------------------------------------------------------
# Session & navigation helpers
# ---------------------------------------------------------------------------

def set_page(page: str) -> None:
    """Update the current page in session state and trigger a rerun."""
    st.session_state.page = page
    st.rerun()

def init_session_state() -> None:
    """Initialize the session state with a default page if not present."""
    if "page" not in st.session_state:
        st.session_state.page = PAGE_DASHBOARD

# ---------------------------------------------------------------------------
# Google Sheets connectivity
# ---------------------------------------------------------------------------

def get_credentials() -> Credentials:
    """
    Create a Credentials instance from Streamlit secrets.

    Expects st.secrets['gcp_service_account'] to contain a valid service account JSON.
    """
    return Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )

@st.cache_resource
def get_sheet() -> gspread.Spreadsheet:
    """Authorize with gspread and open the configured spreadsheet."""
    client = gspread.authorize(get_credentials())
    return client.open(CONFIG.sheet_name)

def load_tab(sheet: gspread.Spreadsheet, tab_name: str) -> pd.DataFrame:
    """Load all records from a worksheet into a DataFrame."""
    try:
        worksheet = sheet.worksheet(tab_name)
        return pd.DataFrame(worksheet.get_all_records())
    except Exception:
        # Return an empty DataFrame if the tab does not exist or fails to load
        return pd.DataFrame()

def append_row(sheet: gspread.Spreadsheet, tab_name: str, row: Dict[str, str]) -> None:
    """Append a row of values to a worksheet and show a success or error message."""
    try:
        worksheet = sheet.worksheet(tab_name)
        worksheet.append_row(list(row.values()))
        st.success("Saved!")
        st.rerun()
    except Exception as exc:
        st.error(f"Unable to save data: {exc}")

# ---------------------------------------------------------------------------
# UI component helpers
# ---------------------------------------------------------------------------

def dashboard_card(title: str, value: int, caption: str, page_to_open: str) -> None:
    """Render a metric card with a button to jump to an add-data page."""
    with st.container(border=True):
        st.subheader(title)
        st.markdown(f"<h1>{value}</h1>", unsafe_allow_html=True)
        st.caption(caption)
        st.button(
            "➕ Add New Data",
            use_container_width=True,
            on_click=set_page,
            args=(page_to_open,),
        )

def render_nav_buttons() -> None:
    """Render navigation buttons to switch between add‑data forms."""
    st.markdown("### Jump to another data entry")
    col1, col2, col3 = st.columns(3)
    col1.button("Attendance", on_click=set_page, args=(PAGE_ADD_ATTENDANCE,))
    col2.button("Guests", on_click=set_page, args=(PAGE_ADD_GUESTS,))
    col3.button("Next Steps", on_click=set_page, args=(PAGE_ADD_NEXT_STEPS,))

def add_attendance_form(sheet: gspread.Spreadsheet) -> None:
    """Display the attendance submission form."""
    st.subheader("➕ Add Church Attendance")
    with st.form("attendance_form"):
        date = st.date_input("Service Date")
        count = st.number_input("Attendance Count", min_value=0, step=1)
        if st.form_submit_button("Save Attendance"):
            append_row(
                sheet,
                CONFIG.attendance_tab,
                {"Service Date": str(date), "Attendance Count": int(count)},
            )

def add_guest_form(sheet: gspread.Spreadsheet) -> None:
    """Display the new guest submission form."""
    st.subheader("➕ Add New Guest")
    with st.form("guest_form"):
        name = st.text_input("Guest Name")
        visit_date = st.date_input("Visit Date")
        contact = st.text_input("Contact Info (optional)")
        if st.form_submit_button("Save Guest"):
            append_row(
                sheet,
                CONFIG.guests_tab,
                {"Guest Name": name, "Visit Date": str(visit_date), "Contact Info": contact},
            )

def add_next_step_form(sheet: gspread.Spreadsheet) -> None:
    """Display the next‑step submission form."""
    st.subheader("➕ Add Next Step")
    with st.form("next_steps_form"):
        name = st.text_input("Name")
        step = st.text_input("Next Step")
        date = st.date_input("Date")
        if st.form_submit_button("Save Next Step"):
            append_row(
                sheet,
                CONFIG.next_steps_tab,
                {"Name": name, "Next Step": step, "Date": str(date)},
            )

def render_previews(attendance: pd.DataFrame, guests: pd.DataFrame, next_steps: pd.DataFrame) -> None:
    """Display preview tables for all three metrics."""
    with st.container(border=True):
        st.subheader("📊 Attendance Records")
        if attendance.empty:
            st.info("No attendance data yet.")
        else:
            st.dataframe(attendance, use_container_width=True)

    with st.container(border=True):
        st.subheader("👋 New Guests")
        if guests.empty:
            st.info("No guest data yet.")
        else:
            st.dataframe(guests, use_container_width=True)

    with st.container(border=True):
        st.subheader("➡️ Next Steps")
        if next_steps.empty:
            st.info("No next steps data yet.")
        else:
            st.dataframe(next_steps, use_container_width=True)

def render_footer() -> None:
    """Render the footer text."""
    st.markdown(
        "<p style='text-align:center;color:#6b7280;font-weight:600;'>"
        "KeepTrek • Church Metrics Made Meaningful</p>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------

def main() -> None:
    """Main entry point for the Streamlit application."""
    st.set_page_config(page_title="KeepTrek Dashboard", layout="wide", page_icon="📊")

    # Apply custom CSS styling
    st.markdown(
        """
        <style>
        body { background: linear-gradient(180deg, #f7fbfd, #fdfefe); }
        h1, h2, h3 { color: #054063; }
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

    init_session_state()
    sheet = get_sheet()

    # Load data once
    attendance_df = load_tab(sheet, CONFIG.attendance_tab)
    guests_df = load_tab(sheet, CONFIG.guests_tab)
    next_steps_df = load_tab(sheet, CONFIG.next_steps_tab)

    # Header with logo
    logo = Image.open("assets/keeptrek_logo.png")
    spacer, center, spacer2 = st.columns([1, 2, 1])
    with center:
        st.image(logo, width=720)
        st.markdown(
            "<p style='text-align:center;color:#47919e;font-weight:700;'>"
            "Measuring Meaningful Metrics</p>",
            unsafe_allow_html=True,
        )

    # Metric cards at top
    col1, col2, col3 = st.columns(3)
    with col1:
        dashboard_card(
            "Church Attendance",
            int(attendance_df["Attendance Count"].sum()) if "Attendance Count" in attendance_df.columns else 0,
            "Total attendance (all services)",
            PAGE_ADD_ATTENDANCE,
        )
    with col2:
        dashboard_card(
            "New Guests",
            len(guests_df),
            "Total new guests",
            PAGE_ADD_GUESTS,
        )
    with col3:
        dashboard_card(
            "Next Steps",
            len(next_steps_df),
            "People taking next steps",
            PAGE_ADD_NEXT_STEPS,
        )

    st.divider()

    # Routing logic
    current_page = st.session_state.page
    if current_page == PAGE_DASHBOARD:
        render_previews(attendance_df, guests_df, next_steps_df)
    elif current_page == PAGE_ADD_ATTENDANCE:
        add_attendance_form(sheet)
        render_nav_buttons()
    elif current_page == PAGE_ADD_GUESTS:
        add_guest_form(sheet)
        render_nav_buttons()
    elif current_page == PAGE_ADD_NEXT_STEPS:
        add_next_step_form(sheet)
        render_nav_buttons()

    render_footer()

if __name__ == "__main__":
    main()
