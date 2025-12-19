import streamlit as st
import numpy as np
import re
import os
from io import BytesIO
from datetime import datetime
from PIL import Image, ImageOps

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

def extract_text_right(words, anchor_label, max_dist=350, y_tol=18):
    """Extract words appearing to the RIGHT of a label."""
    for w in words:
        if w["text"].upper() == anchor_label:
            ax = w["x2"]
            ay = (w["y1"] + w["y2"]) / 2
            parts = [
                t["text"]
                for t in words
                if t["x1"] > ax
                and abs(((t["y1"] + t["y2"]) / 2) - ay) < y_tol
                and t["x1"] < ax + max_dist
            ]
            return normalize(" ".join(parts))
    return ""

def checkbox_score(img, word):
    """Measure ink intensity LEFT of label."""
    h, w = img.shape
    box_h = word["y2"] - word["y1"]
    x2 = max(0, word["x1"] - 5)
    x1 = max(0, x2 - box_h * 4)
    y1 = max(0, word["y1"] - 6)
    y2 = min(h, word["y2"] + 6)
    region = img[y1:y2, x1:x2]
    return ink_density(region)

def strongest_checked(img, words, labels, min_score=0.04):
    scores = {}
    for label in labels:
        for w in words:
            if w["text"].upper() == label:
                score = checkbox_score(img, w)
                scores[label] = score
    if not scores:
        return []
    return [
        k for k, v in scores.items()
        if v == max(scores.values()) and v > min_score
    ]

def multiple_checked(img, words, labels, min_score=0.04):
    found = []
    for label in labels:
        for w in words:
            if w["text"].lower() == label.lower():
                if checkbox_score(img, w) > min_score:
                    found.append(label)
    return found

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

    # =================================================
    # Image Normalize (rotation safe)
    # =================================================
    pil_img = Image.open(BytesIO(file_bytes))
    pil_img = ImageOps.exif_transpose(pil_img)

    if pil_img.width > pil_img.height:
        pil_img = pil_img.rotate(90, expand=True)

    buffer = BytesIO()
    pil_img.save(buffer, format="JPEG")
    file_bytes = buffer.getvalue()

    st.image(pil_img, use_container_width=True)

    # =================================================
    # OCR
    # =================================================
    image = vision.Image(content=file_bytes)
    response = client.text_detection(image=image)

    if not response.text_annotations:
        st.stop()

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
    # Image for Ink Detection
    # =================================================
    gray = pil_img.convert("L")
    img = np.array(gray)

    # =================================================
    # FIELD EXTRACTION (ANCHOR BASED)
    # =================================================
    name = extract_text_right(words, "NAME")
    phone = extract_text_right(words, "PHONE")
    email = extract_text_right(words, "EMAIL")

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

    detected_groups = multiple_checked(img, words, GROUPS)
    detected_teams = multiple_checked(img, words, TEAMS)
    detected_age = strongest_checked(img, words, AGES)
    detected_age = detected_age[0] if detected_age else "ADULT"

    # =================================================
    # REVIEW & CONFIRM UI
    # =================================================
    st.subheader("📋 Review & Confirm")

    with st.form("confirm"):
        name_i = st.text_input("Name", name)
        phone_i = st.text_input("Phone", phone)
        email_i = st.text_input("Email", email)

        age_i = st.radio("Age Group", AGES, AGES.index(detected_age))

        st.markdown("### Next Steps")
        group_i = {g: st.checkbox(g, g in detected_groups) for g in GROUPS}

        st.markdown("### Teams")
        team_i = {t: st.checkbox(t, t in detected_teams) for t in TEAMS}

        submit = st.form_submit_button("Confirm Entry")

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
