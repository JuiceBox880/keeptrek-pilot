import streamlit as st
from datetime import datetime
import os
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
# Handle Upload + OCR
# -----------------------------
if uploaded_file is not None:
    os.makedirs("uploads", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = f"uploads/{timestamp}_{uploaded_file.name}"

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success("Card saved to the cloud.")
    st.image(uploaded_file, caption="Uploaded Card", use_container_width=True)

    # -------------------------
    # OCR STEP
    # -------------------------
    st.subheader("Extracted Text")
    st.write("Running OCR…")

    image = vision.Image(content=uploaded_file.getvalue())
    response = client.text_detection(image=image)
    annotations = response.text_annotations

    if not annotations:
        st.warning("No text detected.")
    else:
        # -------------------------------------------------
        # RAW OCR (for debugging)
        # -------------------------------------------------
        raw_text = annotations[0].description
        st.text(raw_text)

                # -------------------------------------------------
        # COLLECT WORDS WITH COORDINATES
        # -------------------------------------------------
        words = []
        for ann in annotations[1:]:
            box = ann.bounding_poly.vertices
            center_x = sum(v.x for v in box) / 4
            center_y = sum(v.y for v in box) / 4

            words.append({
                "text": ann.description.strip(),
                "x": center_x,
                "y": center_y
            })

        # -------------------------------------------------
        # IDENTIFY HANDWRITING CLUSTERS
        # (heuristic: mixed case or numbers)
        # -------------------------------------------------
        handwriting = [
            w for w in words
            if any(c.isdigit() for c in w["text"])
            or any(c.islower() for c in w["text"])
        ]

        # -------------------------------------------------
        # FORM OPTIONS (from this card)
        # -------------------------------------------------
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

        def nearest_handwriting(label):
            label_words = [w for w in words if w["text"].lower() in label.lower()]
            if not label_words:
                return None

            lw = label_words[0]
            min_dist = 99999

            for hw in handwriting:
                dist = ((lw["x"] - hw["x"])**2 + (lw["y"] - hw["y"])**2) ** 0.5
                min_dist = min(min_dist, dist)

            return min_dist

        # -------------------------------------------------
        # DETECT SELECTED OPTIONS BY PROXIMITY
        # -------------------------------------------------
        DIST_THRESHOLD = 80

        selected_groups = [
            g for g in GROUP_OPTIONS
            if nearest_handwriting(g) and nearest_handwriting(g) < DIST_THRESHOLD
        ]

        selected_teams = [
            t for t in TEAM_OPTIONS
            if nearest_handwriting(t) and nearest_handwriting(t) < DIST_THRESHOLD
        ]

        age_group = None
        for age in AGE_OPTIONS:
            if nearest_handwriting(age) and nearest_handwriting(age) < DIST_THRESHOLD:
                age_group = age

        # -------------------------------------------------
        # DISPLAY PARSED RESULTS
        # -------------------------------------------------
        st.subheader("Parsed Fields")

        st.write("**Selected Groups:**")
        st.write(selected_groups or "—")

        st.write("**Selected Teams:**")
        st.write(selected_teams or "—")

        st.write("**Age Group:**", age_group or "—")
