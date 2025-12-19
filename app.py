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

def checkbox_checked(img, label_word):
    """
    Looks LEFT of a label for ANY handwritten mark:
    dot, x, check, slash.
    """
    h, w = img.shape
    box_h = label_word["y2"] - label_word["y1"]

    x2 = max(0, label_word["x1"] - 5)
    x1 = max(0, x2 - box_h * 6)      # wider search
    y1 = max(0, label_word["y1"] - box_h)
    y2 = min(h, label_word["y2"] + box_h)

    region = img[y1:y2, x1:x2]

    density = ink_density(region)
    return density > 0.06            # forgiving threshold

def extract_text_near(words, anchor, max_dist=350):
    for w in words:
        if w["text"].upper() == anchor:
            ax = w["x2"]
            ay = w["y1"]
            nearby = [
                t["text"] for t in words
                if t["x1"] > ax
                and abs(t["y1"] - ay) < 25
                and t["x1"] < ax + max_dist
            ]
            return " ".join(nearby)
    return ""

def strongest_mark(img, words, labels):
    scores = {}
    for label in labels:
        for w in words:
            if w["text"].upper() == label:
                x1 = max(0, w["x1"] - 150)
                x2 = w["x1"] - 5
                y1 = max(0, w["y1"] - 15)
                y2 = min(img.shape[0], w["y2"] + 15)
                region = img[y1:y2, x1:x2]
                scores[label] = ink_density(region)
    return max(scores, key=scores.get) if scores else ""

# =====================================================
# Upload
# =====================================================
uploaded_file = st.file_uploader("Upload card image", ["jpg", "jpeg", "png"])

if uploaded_file is None:
    st.stop()

# =====================================================
# Read + Normalize Image (ONCE)
# =====================================================
file_bytes = uploaded_file.read()

pil_img = Image.open(BytesIO(file_bytes))
pil_img = ImageOps.exif_transpose(pil_img)

if pil_img.width > pil_img.height:
    pil_img = pil_img.rotate(90, expand=True)

buffer = BytesIO()
pil_img.save(buffer, format="JPEG")
file_bytes = buffer.getvalue()

st.image(pil_img, use_container_width=True)

# =====================================================
# Save copy
# =====================================================
os.makedirs("uploads", exist_ok=True)
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
with open(f"uploads/{ts}_{uploaded_file.name}", "wb") as f:
    f.write(file_bytes)

# =====================================================
# OCR
# =====================================================
image = vision.Image(content=file_bytes)
response = client.text_detection(image=image)

if not response.text_annotations:
    st.warning("No text detected.")
    st.stop()

full_text = normalize(response.full_text_annotation.text)

# =====================================================
# Prep image for ink detection
# =====================================================
gray = pil_img.convert("L")
img = np.array(gray)

# =====================================================
# Word boxes
# =====================================================
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

# =====================================================
# Anchored field extraction
# =====================================================
name = extract_text_near(words, "NAME")
phone = extract_text_near(words, "PHONE")

emails = re.findall(
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    full_text.replace(" ", "")
)
email = emails[0] if emails else ""

# =====================================================
# Options
# =====================================================
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
    if any(checkbox_checked(img, w) for w in words if w["text"] == g)
]

detected_teams = [
    t for t in TEAMS
    if any(checkbox_checked(img, w) for w in words if w["text"] == t)
]

detected_age = strongest_mark(img, words, AGES) or "ADULT"

# =====================================================
# Review & Confirm (Editable)
# =====================================================
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

    submitted = st.form_submit_button("Confirm Entry")

if submitted:
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
