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
        # COLLECT WORDS WITH BOUNDING BOXES
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
        # HANDWRITTEN FIELDS (regex-based)
        # -------------------------------------------------
