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
st.write("Upload a guest card. The robots will try their best.")

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
PRINTED_BLACKLIST = {
    "get baptized", "foundation class", "community group",
    "women’s bible study", "men’s bible study",
    "coffee crew", "parking lot team",
    "sanctuary reset team", "tech assistant",
    "event setup/clean up",
    "important", "info", "name", "phone", "email"
}

def normalize(text):
    return re.sub(r"\s+", " ", text).strip()

def ink_density(img, region):
    if region.size == 0:
        return 0
    return np.mean(region < 170)

def checkbox_region(img, word, offset=90):
    h, w = img.shape
    x2 = max(0, word["x1"] - 10)
    x1 = max(0, x2 - offset)
    y1 = max(0, word["y1"] - 5)
    y2 = min(h, word["y2"] + 5)
    return img[y1:y2, x1:x2]

def checkbox_checked(img, word):
    region = checkbox_region(img, word)
    return ink_density(img, region) > 0.12

def strongest_mark(img, words, labels):
    scores = {}
    for label in labels:
        for w in words:
            if w["text"].upper() == label:
                region = checkbox_region(img, w)
                scores[label] = ink_density(img, region)
    return max(scores, key=scores.get) if scores else ""

def extract_handwritten_name(words):
    candidates = []
    for w in words:
        t = w["text"].lower()
        if t in PRINTED_BLACKLIST:
            continue
        if re.match(r"[A-Za-z]{3,}", w["text"]):
            candidates.append(w["text"])
    return max(candidates, key=len) if candidates else ""

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
    path = f"uploads/{ts}_{uploaded_file.name}"
    with open(path, "wb") as f:
        f.write(file_bytes)

    st.image(uploaded_file, use_container_width=True)

    # =================================================
    # OCR
    # =================================================
    image = vision.Image(content=file_bytes)
    response = client.text_detection(image=image)

    if not response.text_annotations:
        st.error("No text detected. The machines are confused.")
        st.stop()

    full_text = normalize(response.full_text_annotation.text)

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
    # Extract Fields
    # =================================================
    name = extract_handwritten_name(words)

    phone_match = re.search(r"\b\d{3}[\s.-]?\d{3}[\s.-]?\d{4}\b", full_text)
    email_match = re.search(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        full_text
    )

    phone = phone_match.group(0) if phone_match else ""
    email = email_match.group(0) if email_match else ""

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

    detected_age = strongest_mark(img, words, AGES) or "ADULT"

    # =================================================
    # Review UI
    # =================================================
    st.subheader("📋 Review & Confirm")

    with st.form("confirm_form"):
        name_i = st.text_input("Name", value=name)
        phone_i = st.text_input("Phone", value=phone)
        email_i = st.text_input("Email", value=email)

        age_i = st.radio(
            "Age Group",
            AGES,
            index=AGES.index(detected_age)
        )

        st.markdown("### Groups")
        group_i = {g: st.checkbox(g, g in detected_groups) for g in GROUPS}

        st.markdown("### Teams")
        team_i = {t: st.checkbox(t, t in detected_teams) for t in TEAMS}

        submitted = st.form_submit_button("✅ Confirm Entry")

    if submitted:
        st.success("Saved. Humans approved it. That still matters.")
        st.json({
            "name": name_i,
            "phone": phone_i,
            "email": email_i,
            "age_group": age_i,
            "groups": [g for g, v in group_i.items() if v],
            "teams": [t for t, v in team_i.items() if v],
            "timestamp": ts
        })
