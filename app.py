import streamlit as st
from datetime import datetime
import os
from io import BytesIO
import re
import numpy as np
from PIL import Image

from google.cloud import vision
from google.oauth2 import service_account

# =====================================================
# App Config
# =====================================================
st.set_page_config(page_title="KeepTrek Pilot", layout="centered")

st.title("🏕️ KeepTrek Pilot")
st.write("Upload a guest or info card, review the details, and confirm the entry.")

# =====================================================
# Load Google Vision Credentials
# =====================================================
credentials = service_account.Credentials.from_service_account_info(
    dict(st.secrets["google"])
)
client = vision.ImageAnnotatorClient(credentials=credentials)

# =====================================================
# Helper Functions
# =====================================================
def words_below(label, words, y_padding=10):
    label_words = [w for w in words if w["text"].upper() == label]
    if not label_words:
        return []
    lw = label_words[0]
    return [w for w in words if w["y1"] > lw["y2"] + y_padding]

def ink_density(img, x1, y1, x2, y2):
    h, w = img.shape
    x1, x2 = max(0, x1), min(w, x2)
    y1, y2 = max(0, y1), min(h, y2)
    region = img[y1:y2, x1:x2]
    if region.size == 0:
        return 0
    return np.mean(region < 200)

def mark_present(img, x1, y1, x2, y2, threshold=0.12):
    h, w = img.shape
    x1, x2 = max(0, x1), min(w, x2)
    y1, y2 = max(0, y1), min(h, y2)
    region = img[y1:y2, x1:x2]
    if region.size == 0:
        return False

    dark = region < 200
    density = np.mean(dark)

    if density < 0.03:
        return False

    rows = np.sum(dark, axis=1) > 2
    cols = np.sum(dark, axis=0) > 2
    stroke_score = np.sum(rows) + np.sum(cols)

    return density > threshold or stroke_score > 6

# =====================================================
# File Upload
# =====================================================
uploaded_file = st.file_uploader(
    "Upload an info card image",
    type=["jpg", "jpeg", "png"]
)

# =====================================================
# MAIN LOGIC
# =====================================================
if uploaded_file is not None:

    # ---- Read file once
    file_bytes = bytes(uploaded_file.getbuffer())

    # ---- Save file
    os.makedirs("uploads", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = f"uploads/{timestamp}_{uploaded_file.name}"
    with open(file_path, "wb") as f:
        f.write(file_bytes)

    st.success("Card uploaded successfully.")
    st.image(uploaded_file, use_container_width=True)

    # ---- OCR
    image = vision.Image(content=file_bytes)
    response = client.text_detection(image=image)
    annotations = response.text_annotations

    if not annotations:
        st.warning("No text detected on this card.")
        st.stop()

    # ---- Image for ink detection
    pil_img = Image.open(BytesIO(file_bytes)).convert("L")
    img = np.array(pil_img)

    # ---- Collect words
    words = []
    for ann in annotations[1:]:
        box = ann.bounding_poly.vertices
        words.append({
            "text": ann.description.strip(),
            "x1": min(v.x for v in box),
            "x2": max(v.x for v in box),
            "y1": min(v.y for v in box),
            "y2": max(v.y for v in box),
        })

    # =================================================
    # IMPORTANT INFO (anchored below "IMPORTANT")
    # =================================================
    important_words = words_below("IMPORTANT", words)
    important_text = " ".join(w["text"] for w in important_words)

    name_match = re.search(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b", important_text)
    phone_match = re.search(r"\b\d{3}\s?\d{3}\s?\d{4}\b", important_text)
    email_match = re.search(
        r"[A-Za-z0-9._%+-]+ *@ *[A-Za-z0-9.-]+ *\. *[A-Za-z]{2,}",
        important_text
    )

    name = name_match.group(0) if name_match else ""
    phone = phone_match.group(0).replace(" ", "") if phone_match else ""
    email = email_match.group(0).replace(" ", "") if email_match else ""

    # =================================================
    # GROUP / TEAM / AGE OPTIONS
    # =================================================
    GROUP_OPTIONS = [
        "Get Baptized",
        "Foundation Class",
        "Community Group",
        "Women's Bible Study",
        "Men's Bible Study"
    ]

    TEAM_OPTIONS = [
        "Coffee Crew",
        "Parking Lot Team",
        "Sanctuary Reset Team",
        "Tech Assistant",
        "Event Setup/Clean Up"
    ]

    AGE_OPTIONS = ["CHILD", "TEEN", "ADULT"]

    def option_checked(label):
        for w in words:
            if w["text"].lower() == label.lower():
                return mark_present(
                    img,
                    w["x1"] - 80,
                    w["y1"] - 5,
                    w["x1"] - 10,
                    w["y2"] + 5
                )
        return False

    detected_groups = [g for g in GROUP_OPTIONS if option_checked(g)]
    detected_teams = [t for t in TEAM_OPTIONS if option_checked(t)]

    detected_age = ""
    for age in AGE_OPTIONS:
        if option_checked(age):
            detected_age = age

    # =================================================
    # REVIEW & CONFIRM UI (EDITABLE)
    # =================================================
    st.subheader("📋 Review & Confirm Information")

    with st.form("confirm_form"):
        st.markdown("### Important Info")
        name_input = st.text_input("Name", value=name)
        phone_input = st.text_input("Phone", value=phone)
        email_input = st.text_input("Email", value=email)

        st.markdown("### Age Group")
        age_input = st.radio("Select one", AGE_OPTIONS, index=AGE_OPTIONS.index(detected_age) if detected_age in AGE_OPTIONS else 2)

        st.markdown("### Groups")
        group_inputs = {
            g: st.checkbox(g, value=(g in detected_groups))
            for g in GROUP_OPTIONS
        }

        st.markdown("### Teams")
        team_inputs = {
            t: st.checkbox(t, value=(t in detected_teams))
            for t in TEAM_OPTIONS
        }

        submitted = st.form_submit_button("✅ Confirm Entry")

    if submitted:
        st.success("Entry confirmed and ready to save.")
        st.write({
            "name": name_input,
            "phone": phone_input,
            "email": email_input,
            "age_group": age_input,
            "groups": [g for g, v in group_inputs.items() if v],
            "teams": [t for t, v in team_inputs.items() if v],
            "timestamp": timestamp
        })
