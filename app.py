from typing import Dict, Tuple
import streamlit as st
import pandas as pd
from PIL import Image
import gspread
from google.oauth2.service_account import Credentials

# ============================================================
# CONFIG
# ============================================================
SHEET_NAME = "KeepTrek_Data"

# ============================================================
# TYPES
# ============================================================
MetricValue = Tuple[int, str]

# ============================================================
# PAGE SETUP
# ============================================================
st.set_page_config(
    page_title="KeepTrek Dashboard",
    layout="wide",
    page_icon="📊"
)

# ============================================================
# STYLING
# ============================================================
st.markdown("""
<style>
body {
    background: linear-gradient(180deg, #f7fbfd, #fdfefe);
}
h1,h2,h3 {
    color: #054063;
}
.stButton>button {
    background: linear-gradient(135deg, #179171, #34a94d);
    color: white;
    font-weight: 800;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# GOOGLE SHEETS CONNECTION
# ============================================================
@st.cache_resource
def get_gsheet():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    client = gspread.authorize(creds)
    return client.open(SHEET_NAME)

sheet = get_gsheet()

def load_tab(tab_name: str) -> pd.DataFrame:
    try:
        worksheet = sheet.worksheet(tab_name)
        data = worksheet.get_all_records()
        return pd.DataFrame(data)
    except Exception:
        return pd.DataFrame()

attendance_df = load_tab("Attendance")
guests_df = load_tab("New_Guests")
next_steps_df = load_tab("Next_Steps")

# ============================================================
# METRIC CALCULATIONS
# ============================================================
def safe_sum(df, col):
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
        "<p style='text-align:center;color:#47919e;font-weight:700;'>Measuring Meaningful Metrics</p>",
        unsafe_allow_html=True
    )

# ============================================================
# DASHBOARD CARDS
# ============================================================
col1, col2, col3 = st.columns(3)

with col1:
    st.container(border=True)
    st.subheader("Church Attendance")
    st.markdown(f"<h1>{attendance_total}</h1>", unsafe_allow_html=True)
    st.caption("Total attendance (all services)")

with col2:
    st.container(border=True)
    st.subheader("New Guests")
    st.markdown(f"<h1>{new_guest_total}</h1>", unsafe_allow_html=True)
    st.caption("Total new guests")

with col3:
    st.container(border=True)
    st.subheader("Next Steps")
    st.markdown(f"<h1>{next_steps_total}</h1>", unsafe_allow_html=True)
    st.caption("People taking next steps")

st.divider()

# ============================================================
# DATA PREVIEW SECTIONS
# ============================================================
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
# FOOTER
# ============================================================
st.markdown(
    "<p style='text-align:center;color:#6b7280;font-weight:600;'>KeepTrek • Church Metrics Made Meaningful</p>",
    unsafe_allow_html=True
)
