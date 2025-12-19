import streamlit as st
import numpy as np
import re
import os
from io import BytesIO
from datetime import datetime
from PIL import Image

from google.cloud import vision
from google.oauth2 import service_account

# =====================================================
# App Config
# =====================================================
st.set_page_config(page_title="KeepTrek Pilot", layout="centered")
st.title("🏕️ KeepTrek Pilot")
st.write("Upload a guest card. We will coerce it into compliance.")

# =====================================================
# Google Vision Client
# =====================================================
credentials = service_account.Credentials.from_service_account_info(
    dict(st.secrets["google"])
)
client = vision.ImageAnnotatorClient(credentials=credentials)

# =====================================================
# Helpers
# =====================================================
def normalize_email_text(text):
    text = re.sub(r"\s*@\s*", "@", text)
    text = re.sub(r"\s*\.\s*", ".", text)
    return text

def ink_score(region):
    if region.size == 0:
        return 0
    dark = region < 175
    return np.mean(dark)

def checkbox_region(img, word, offset=120):
    h, w = img.shape
    x2 = max(0, word["x1"] - 10)
    x1 = max(0, x2 - offset)
    y1 = max(0, word["y1"] - 8)
    y2 = min(h, word["y2"] + 8)
    return img[y1:y2, x1:x2]

def checkbox_checked(img, word):
    region = checkbox_region(img, word)
    score = ink_score(region)

    # diagonal stroke detection
    diag = np.trace(region < 175) if region.size else 0
    return score > 0.06 or diag > 5

def strongest_mark(img, words, labels):
    scores = {}
    for label in labels:
        for w in words:
            if w["text"].upper() == label:
                region = checkbox_region(img, w)
                scores[label] = ink_score(region)
    return max(scores, key=scores.get) if scores else ""

def extract_field_right(words, label, max_words=4):
    for w in words:
        if w["text"].upper() == label:
            y_mid = (w["y1"] + w["y2"]) / 2
            candidates = [
                x for x in words
                if x["x1"] > w["x2"]
                and abs(((x["y1"] + x["y2"]) / 2) - y_mid) < 20
            ]
            candidates = sorted(candidates, key=lambda x: x["x1"])
            return " ".join(c["text"] for c in candidates[:max_words])
    return ""

# =====================================================
# Upload
# =====================================================
uploaded_file = st.file_uploader(
    "Upload an info card image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file:
    file_bytes = uploaded_file.read()

    os.makedirs("uploads", exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"uploads/{ts}_{uploaded_file.name}", "wb") as f:
        f.write(file_bytes)

    st.image(uploaded_file, use_container_width=True)

    # =================================================
    # OCR
    # =================================================
    image = vision.Image(content=file_bytes)
    response = client.text_detection(image=image)

    if not response.text_annotations:
        st.error("No text detected.")
        st.stop()

    full_text = normalize_email_text(
        response.full_text_annotation.text
    )

    # =================================================
    # Prep Image
    # =================================================
    gray = Image.open(BytesIO(file_bytes)).convert("L")
    img = np.array(gray)

    # =================================================
    # Word Boxes
    # =================================================
    words = []
    for ann in response.text_annotations[1:]:
        v = ann.bounding_poly.vertices
        words.append({
            "text": ann.description.strip(),
            "x1": min(p.x for p in v),
            "x2": max(p.x for p in v),
            "y1": min(p.y for p in v),
            "y2": max(p.y for p in v),
        })

    # =================================================
    # Extract Anchored Fields
    # =================================================
    name = extract_field_right(words, "NAME", max_words=3)
    phone = extract_field_right(words, "PHONE", max_words=3)
    email = extract_field_right(words, "EMAIL", max_words=4)

    phone_match = re.search(r"\d{3}[\s.-]?\d{3}[\s.-]?\d{4}", phone)
    phone = phone_match.group(0) if phone_match else phone

    email_match = re.search(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        email
    )
    email = email_match.group(0) if email_match else email

    # =================================================
    # Options
    # =================================================
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

    detected_groups = [
        g for g in GROUPS
        if any(
            checkbox_checked(img, w)
            for w in words if w["text"].lower() == g.lower()
        )
    ]

    detected_teams = [
        t for t in TEAMS
        if any(
            checkbox_checked(img, w)
            for w in words if w["text"].lower() == t.lower()
        )
    ]

    detected_age = strongest_mark(img, words, AGES)

    # =================================================
    # Review UI
    # =================================================
    st.subheader("📋 Review & Confirm")

    with st.form("confirm"):
        name_i = st.text_input("Name", name)
        phone_i = st.text_input("Phone", phone)
        email_i = st.text_input("Email", email)

        age_i = st.radio(
            "Age Group",
            AGES,
            index=AGES.index(detected_age) if detected_age else 2
        )

        st.markdown("### Groups")
        group_i = {g: st.checkbox(g, g in detected_groups) for g in GROUPS}

        st.markdown("### Teams")
        team_i = {t: st.checkbox(t, t in detected_teams) for t in TEAMS}

        submitted = st.form_submit_button("Confirm Entry")

    if submitted:
        st.success("Saved. The paper has been defeated.")
        st.json({
            "name": name_i,
            "phone": phone_i,
            "email": email_i,
            "age_group": age_i,
            "groups": [g for g, v in group_i.items() if v],
            "teams": [t for t, v in team_i.items() if v],
            "timestamp": ts
        })
