import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import base64
import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime, date

# =========================
# 🔐 Environment Setup
# =========================
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("❌ OPENAI_API_KEY missing.")
    st.stop()

client = OpenAI(api_key=api_key)

# =========================
# 🖥️ Page Setup
# =========================
st.set_page_config(
    page_title="KeepTrek Guest Tracker",
    layout="wide",
    page_icon="🛤️"
)
st.title("📋 KeepTrek Guest Tracker")

tab1, tab2 = st.tabs(["📝 Guest Entry", "📋 View Guests"])

# =========================
# 🧠 Session State
# =========================
st.session_state.setdefault("processed_files", set())
st.session_state.setdefault("manual_guest_queue", [])

# =========================
# 📄 Google Sheets Setup
# =========================
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_file("creds.json", scopes=scope)
gc = gspread.authorize(creds)
sheet = gc.open("KeepTrek_TrackingData").sheet1

# =========================
# 🧱 Column Definition
# =========================
COLUMNS = [
    "Name",
    "Email",
    "Phone",
    "Age Group",
    "First Visit Date",
    "Get Baptized",
    "Foundations Class",
    "Community Group",
    "Women's Ministry",
    "Men's Bible Study",
    "Coffee Crew",
    "Parking Lot Team",
    "Sanctuary Reset Team",
    "Tech Assistant",
    "Event Setup / Clean Up",
    "Notes"
]

# Ensure headers exist
existing_headers = sheet.row_values(1)
if existing_headers != COLUMNS:
    sheet.clear()
    sheet.append_row(COLUMNS)

records = sheet.get_all_records()
data = pd.DataFrame(records) if records else pd.DataFrame(columns=COLUMNS)

# =========================
# 📝 TAB 1: Manual Entry
# =========================
with tab1:
    st.subheader("➕ Manually Add a New Guest")

    with st.form("manual_guest_form"):
        name = st.text_input("👤 Name")
        email = st.text_input("📧 Email")
        phone = st.text_input("📱 Phone")

        age_group = st.radio(
            "🎂 Age Group",
            ["Child", "Teen", "Adult"],
            horizontal=True
        )

        st.markdown("### ✅ Areas of Interest")

        checks = {
            "Get Baptized": st.checkbox("Get Baptized"),
            "Foundations Class": st.checkbox("Foundations Class"),
            "Community Group": st.checkbox("Community Group"),
            "Women's Ministry": st.checkbox("Women's Ministry"),
            "Men's Bible Study": st.checkbox("Men's Bible Study"),
            "Coffee Crew": st.checkbox("Coffee Crew"),
            "Parking Lot Team": st.checkbox("Parking Lot Team"),
            "Sanctuary Reset Team": st.checkbox("Sanctuary Reset Team"),
            "Tech Assistant": st.checkbox("Tech Assistant"),
            "Event Setup / Clean Up": st.checkbox("Event Setup / Clean Up"),
        }

        notes = st.text_area("🗒️ Notes / Comments")

        submitted = st.form_submit_button("✅ Add Guest")

        if submitted:
            if not name or not email:
                st.warning("Please provide at least a name and email.")
            else:
                row = {
                    "Name": name,
                    "Email": email,
                    "Phone": phone,
                    "Age Group": age_group,
                    "First Visit Date": date.today().strftime("%Y-%m-%d"),
                    **{k: "✅" if v else "" for k, v in checks.items()},
                    "Notes": notes
                }
                st.session_state.manual_guest_queue.append(row)
                st.success(f"🕒 {name} added to queue.")

    if st.session_state.manual_guest_queue:
        st.subheader("📄 Ready to Submit")
        st.dataframe(pd.DataFrame(st.session_state.manual_guest_queue), use_container_width=True)

        if st.button("📤 Submit All to Google Sheet"):
            for guest in st.session_state.manual_guest_queue:
                sheet.append_row([guest.get(col, "") for col in COLUMNS])
            st.success("✅ Guests added!")
            st.session_state.manual_guest_queue.clear()

    # =========================
    # 📸 Handwritten Card Upload
    # =========================
    st.markdown("---")
    st.subheader("🧠 Upload a Handwritten Guest Card")

    manual_review = st.toggle("🕵️ Manual Review Mode", value=True)
    upl
