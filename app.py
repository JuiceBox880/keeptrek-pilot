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
    texts = response.text_annotations

    if not texts:
        st.warning("No text detected.")
    else:
        # --- RAW OCR TEXT ---
        raw_text = texts[0].description
        st.text(raw_text)

        # --- NORMALIZE INTO LINES ---
        lines = [line.strip() for line in raw_text.split("\n") if line.strip()]

        # --- HELPER: value after a label ---
        def value_after(label, lines):
            if label in lines:
                idx = lines.index(label)
                if idx + 1 < len(lines):
                    return lines[idx + 1]
            return None

        # --- EXTRACT CORE FIELDS ---
        name = value_after("NAME", lines)
        phone = value_after("PHONE", lines)
        email = value_after("EMAIL", lines)

        # --- AGE GROUP (single select) ---
        age_group = None
        for option in ["CHILD", "TEEN", "ADULT"]:
            if option in lines:
                age_group = option
                break

        # --- DISPLAY PARSED RESULTS ---
        st.subheader("Parsed Fields")
        st.write(f"**Name:** {name or '—'}")
        st.write(f"**Phone:** {phone or '—'}")
        st.write(f"**Email:** {email or '—'}")
        st.write(f"**Age Group:** {age_group or '—'}")
