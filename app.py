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
# MAIN LOGIC (only runs if file exists)
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
    # OCR STEP
    # ---------------------------------
    st.subheader("Extracted Text")
    st.write("Running OCR…")

    image = vision.Image(content=file_bytes)
    response = client.text_detection(image=image)
    annotations = response.text_annotations

    if not annotations:
        st.warning("No text detected.")
    else:
        # ---------------------------------
        # RAW OCR TEXT (debug)
        # ---------------------------------
        raw_text = annotations[0].description
        st.text(raw_text)

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
        full_text = " ".join(w["text"] for w in words)

        name_match = re.search(r"[A-Z][a-z]+ [A-Z][a-z]+", full_text)
        phone_match = re.search(r"\b\d{3}\s?\d{3}\s?\d{4}\b", full_text)
        email_match = re.search(
            r"[A-Za-z0-9._%+-]+@?[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
            full_text
        )

        name = name_match.group(0) if name_match else None
        phone = phone_match.group(0).replace(" ", "") if phone_match else None
        email = email_match.group(0).replace(" ", "") if email_match else None

        # ---------------------------------
        # Checkbox logic (ANY ink = checked)
        # ---------------------------------
        INK_THRESHOLD = 0.05

        def is_checked(label):
            for w in words:
                if w["text"].lower() in label.lower():
                    # checkbox area is LEFT of label
                    region = (
                        w["x1"] - 70,
                        w["y1"],
                        w["x1"] - 5,
                        w["y2"]
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
        # DISPLAY RESULTS (spreadsheet-ready)
        # ---------------------------------
        st.subheader("Parsed Fields")

        st.write(f"**Name:** {name or '—'}")
        st.write(f"**Phone:** {phone or '—'}")
        st.write(f"**Email:** {email or '—'}")
        st.write(f"**Age Group:** {age_group or '—'}")

        st.write("**Selected Groups:**")
        st.write(selected_groups or "—")

        st.write("**Selected Teams:**")
        st.write(selected_teams or "—")
