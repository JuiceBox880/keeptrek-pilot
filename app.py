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
st.write("Upload a guest card. Paper is stubborn. We persist.")

# =====================================================
# Vision Client
# =====================================================
credentials = service_account.Credentials.from_service_account_info(
    dict(st.secrets["google"])
)
client = vision.ImageAnnotatorClient(credentials=credentials)

# =====================================================
# Helpers
# =====================================================
def normalize(text):
    return re.sub(r"\s+", " ", text).strip()

def ink_density(region):
    if region.size == 0:
        return 0
    return np.mean(region < 170)

def region_from_anchor(img, anchor, dx1, dx2, dy=8):
    h, w = img.shape
    x1 = max(0, anchor["x2"] + dx1)
    x2 = min(w, anchor["x2"] + dx2)
    y1 = max(0, anchor["y1"] - dy)
    y2 = min(h, anchor["y2"] + dy)
    return img[y1:y2, x1:x2]

def extract_text_near(words, anchor_word, direction="right", max_dist=350):
    for w in words:
        if w["text"].upper() == anchor_word:
            ax = w["x2"]
            ay1, ay2 = w["y1"], w["y2"]
            candidates = [
                t["text"] for t in words
                if t["x1"] > ax and abs(t["y1"] - ay1) < 20
                and t["x1"] < ax + max_dist
            ]
            return " ".join(candidates)
    return ""

def checkbox_checked(img, label_word):
    box_height = label_word["y2"] - label_word["y1"]
    scan_width = box_height * 4

    x2 = label_word["x1"] - 5
    x1 = max(0, x2 - scan_width)
    y1 = max(0, label_word["y1"] - 6)
    y2 = min(img.shape[0], label_word["y2"] + 6)

    region = img[y1:y2, x1:x2]
    return ink_density(region) > 0.08

def strongest_mark(img, words, labels):
    scores = {}
    for label in labels:
        for w in words:
            if w["text"].upper() == label:
                x1 = max(0, w["x1"] - 120)
                x2 = w["x1"] - 5
                y1 = w["y1"] - 6
                y2 = w["y2"] + 6
                region = img[y1:y2, x1:x2]
                scores[label] = ink_density(region)
    return max(scores, key=scores.get) if scores else ""

# =====================================================
# Upload
# =====================================================
uploaded_file = st.file_uploader("Upload card image", ["jpg", "jpeg", "png"])

if uploaded_file:

    file_bytes = uploaded_file.read()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    os.makedirs("uploads", exist_ok=True)
    with open(f"uploads/{ts}_{uploaded_file.name}", "wb") as f:
        f.write(file_bytes)

    st.image(uploaded_file, use_container_width=True)

    # =================================================
    # OCR
    # =================================================
    image = vision.Image(content=file_bytes)
    response = client.text_detection(image=image)

    if not response.text_annotations:
        st.stop()

    full_text = normalize(response.full_text_annotation.text)

    # =================================================
    # Image Prep
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
    # FIELD EXTRACTION (ANCHOR-BASED)
    # =================================================
    name = extract_text_near(words, "NAME")
    phone = extract_text_near(words, "PHONE")

    email_candidates = re.findall(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        full_text.replace(" ", "")
    )
    email = email_candidates[0] if email_candidates else ""

    # =================================================
    # OPTIONS
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
    # REVIEW
    # =================================================
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
        st.success("Saved. Paper defeated.")
        st.json({
            "name": name_i,
            "phone": phone_i,
            "email": email_i,
            "age": age_i,
            "groups": [g for g, v in group_i.items() if v],
            "teams": [t for t, v in team_i.items() if v],
            "timestamp": ts
        })
