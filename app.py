import streamlit as st
import numpy as np
import re
from io import BytesIO
from PIL import Image
from datetime import datetime
import os

from google.cloud import vision
from google.oauth2 import service_account

# ============================
# App Config
# ============================
st.set_page_config(page_title="KeepTrek Pilot", layout="centered")
st.title("🏕️ KeepTrek Pilot")
st.write("Upload a guest card. We’ll do our best. God handles the rest.")

# ============================
# Vision Client
# ============================
credentials = service_account.Credentials.from_service_account_info(
    dict(st.secrets["google"])
)
client = vision.ImageAnnotatorClient(credentials=credentials)

# ============================
# Helpers
# ============================
def ink_present(img, box, expand=20, threshold=0.08):
    h, w = img.shape
    x1 = max(0, box["x1"] - expand)
    x2 = min(w, box["x2"] + expand)
    y1 = max(0, box["y1"] - expand)
    y2 = min(h, box["y2"] + expand)

    region = img[y1:y2, x1:x2]
    if region.size == 0:
        return False

    dark_pixels = region < 180
    density = np.mean(dark_pixels)
    return density > threshold

def normalize(text):
    return re.sub(r"\s+", " ", text).strip()

# ============================
# Upload
# ============================
uploaded_file = st.file_uploader("Upload card image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    file_bytes = uploaded_file.read()

    os.makedirs("uploads", exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"uploads/{ts}_{uploaded_file.name}"
    with open(path, "wb") as f:
        f.write(file_bytes)

    st.image(uploaded_file, use_container_width=True)

    # ============================
    # OCR
    # ============================
    image = vision.Image(content=file_bytes)
    response = client.text_detection(image=image)

    if not response.text_annotations:
        st.error("OCR failed. The robots see nothing.")
        st.stop()

    full_text = response.full_text_annotation.text
    clean_text = normalize(full_text)

    # ============================
    # Extract Handwritten Fields
    # ============================
    name_match = re.search(r"\b([A-Z][a-z]+ [A-Z][a-z]+)\b", clean_text)
    phone_match = re.search(r"\b(\d{3}[\s.-]?\d{3}[\s.-]?\d{4})\b", clean_text)
    email_match = re.search(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        clean_text
    )

    name = name_match.group(1) if name_match else ""
    phone = phone_match.group(1) if phone_match else ""
    email = email_match.group(0) if email_match else ""

    # ============================
    # Prep Image for Checkbox Detection
    # ============================
    gray = Image.open(BytesIO(file_bytes)).convert("L")
    img = np.array(gray)

    # ============================
    # Collect Word Boxes
    # ============================
    words = []
    for w in response.text_annotations[1:]:
        v = w.bounding_poly.vertices
        words.append({
            "text": w.description.strip(),
            "x1": min(p.x for p in v),
            "x2": max(p.x for p in v),
            "y1": min(p.y for p in v),
            "y2": max(p.y for p in v),
        })

    # ============================
    # Options
    # ============================
    GROUPS = [
        "Get Baptized",
        "Foundation Class",
        "Community Group",
        "Women's Bible Study",
        "Men's Bible Study"
    ]

    TEAMS = [
        "Coffee Crew",
        "Parking Lot Team",
        "Sanctuary Reset Team",
        "Tech Assistant",
        "Event Setup/Clean Up"
    ]

    AGES = ["CHILD", "TEEN", "ADULT"]

    def is_checked(label):
        for w in words:
            if w["text"].lower() == label.lower():
                return ink_present(img, w)
        return False

    detected_groups = [g for g in GROUPS if is_checked(g)]
    detected_teams = [t for t in TEAMS if is_checked(t)]
    detected_age = next((a for a in AGES if is_checked(a)), "ADULT")

    # ============================
    # Review UI
    # ============================
    st.subheader("📋 Review & Confirm")

    with st.form("confirm"):
        name_i = st.text_input("Name", name)
        phone_i = st.text_input("Phone", phone)
        email_i = st.text_input("Email", email)

        age_i = st.radio("Age Group", AGES, AGES.index(detected_age))

        st.markdown("### Groups")
        group_i = {g: st.checkbox(g, g in detected_groups) for g in GROUPS}

        st.markdown("### Teams")
        team_i = {t: st.checkbox(t, t in detected_teams) for t in TEAMS}

        submit = st.form_submit_button("Confirm")

    if submit:
        st.success("Saved. Heaven rejoices. Database too.")
        st.json({
            "name": name_i,
            "phone": phone_i,
            "email": email_i,
            "age": age_i,
            "groups": [g for g, v in group_i.items() if v],
            "teams": [t for t, v in team_i.items() if v],
            "timestamp": ts
        })
