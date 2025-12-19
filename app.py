import streamlit as st
from datetime import datetime
import os
from io import BytesIO
import re
import numpy as np
from PIL import Image

from google.cloud import vision
from google.oauth2 import service_account

# -----------------------------
# App Config
# -----------------------------
st.set_page_config(page_title="KeepTrek Pilot", layout="centered")

st.title("🏕️ KeepTrek Pilot")
st.write("Upload a guest or info card to begin.")

# -----------------------------
# Load Google Vision Credentials
# -----------------------------
credentials = service_account.Credentials.from_service_account_info(
    dict(st.secrets["google"])
)
client = vision.ImageAnnotatorClient(credentials=credentials)

# -----------------------------
# File Upload
# -----------------------------
uploaded_file = st.file_uploader(
    "Upload an info card image",
    type=["jpg", "jpeg", "png"]
)

# -----------------------------
# MAIN LOGIC (runs only if file exists)
# -----------------------------
if uploaded_file is not None:

    # ---------------------------------
    # Read file ONCE (Streamlit-safe)
    # ---------------------------------
    file_bytes = bytes(uploaded_file.getbuffer())

    # ---------------------------------
    # Save uploaded file
    # ---------------------------------
    os.makedirs("uploads", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = f"uploads/{timestamp}_{uploaded_file.name}"

    with open(file_path, "wb") as f:
        f.write(file_bytes)

    st.success("Card saved to the cloud.")
    st.image(uploaded_file, caption="Uploaded Card", use_container_width=True)

    # ---------------------------------
    # OCR STEP (silent)
    # ---------------------------------
    image = vision.Image(content=file_bytes)
    response = client.text_detection(image=image)
    annotations = response.text_annotations

    if not annotations:
        st.warning("No text detected.")
    else:
        # ---------------------------------
        # RAW OCR TEXT (hidden)
        # ---------------------------------
        with st.expander("🔍 View raw OCR text (for debugging)", expanded=False):
            st.text(annotations[0].description)

        # ---------------------------------
        # Load image for ink detection
        # ---------------------------------
        pil_img = Image.open(BytesIO(file_bytes)).convert("L")
        img = np.array(pil_img)

        def ink_density(x1, y1, x2, y2):
            h, w = img.shape
            x1, x2 = max(0, x1), min(w, x2)
            y1, y2 = max(0, y1), min(h, y2)
            region = img[y1:y2, x1:x2]
            if region.size == 0:
                return 0
            return np.mean(region < 200)  # % dark pixels

        # ---------------------------------
        # Collect word bounding boxes
        # ---------------------------------
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

        # ---------------------------------
        # IMPORTANT INFO (handwritten fields)
        # ---------------------------------
        important_words = words_below("IMPORTANT", words)
important_text = " ".join(w["text"] for w in important_words)

name_match = re.search(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b", important_text)
phone_match = re.search(r"\b\d{3}\s?\d{3}\s?\d{4}\b", important_text)
email_match = re.search(
    r"[A-Za-z0-9._%+-]+ *@ *[A-Za-z0-9.-]+ *\. *[A-Za-z]{2,}",
    important_text
)
        def words_below(label, words, y_padding=10):
    """
    Return only words that appear visually BELOW a given label.
    This lets us read the form like a human would.
    """
    label_words = [w for w in words if w["text"].upper() == label]
    if not label_words:
        return []

    lw = label_words[0]

    return [
        w for w in words
        if w["y1"] > lw["y2"] + y_padding
    ]
        name = name_match.group(0) if name_match else None
        phone = phone_match.group(0).replace(" ", "") if phone_match else None
        email = email_match.group(0) if email_match else None

        # ---------------------------------
        # Checkbox logic (handwritten ink only)
        # ---------------------------------
        INK_THRESHOLD = 0.12

        def is_checked(label):
            for w in words:
                if w["text"].lower() == label.lower():
                    region = (
                        w["x1"] - 80,
                        w["y1"] - 5,
                        w["x1"] - 10,
                        w["y2"] + 5
                    )
                    return ink_density(*region) > INK_THRESHOLD
            return False

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

        selected_groups = [g for g in GROUP_OPTIONS if is_checked(g)]
        selected_teams = [t for t in TEAM_OPTIONS if is_checked(t)]

        age_group = None
        for age in AGE_OPTIONS:
            if is_checked(age):
                age_group = age

        # ---------------------------------
        # DISPLAY RESULTS (user-friendly)
        # ---------------------------------
        st.subheader("📋 What we found on this card")

        st.write(f"**Name:** {name or '—'}")
        st.write(f"**Phone:** {phone or '—'}")
        st.write(f"**Email:** {email or '—'}")
        st.write(f"**Age Group:** {age_group or '—'}")

        st.write("**Next Steps Selected:**")
        st.write(selected_groups or "—")

        st.write("**Teams Selected:**")
        st.write(selected_teams or "—")
