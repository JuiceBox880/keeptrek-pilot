import streamlit as st
from datetime import datetime
import os
import json
from google.cloud import vision
from google.oauth2 import service_account

st.set_page_config(page_title="KeepTrek Pilot", layout="centered")

st.title("🏕️ KeepTrek Pilot")
st.write("Upload a guest or info card to begin.")

# --- Load Google Vision credentials from Streamlit Secrets ---
credentials_info = json.loads(
    st.secrets["GOOGLE_APPLICATION_CREDENTIALS_JSON"]
)
credentials = service_account.Credentials.from_service_account_info(
    credentials_info
)
client = vision.ImageAnnotatorClient(credentials=credentials)

uploaded_file = st.file_uploader(
    "Upload an info card image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    os.makedirs("uploads", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = f"uploads/{timestamp}_{uploaded_file.name}"

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success("Card saved to the cloud.")
    st.image(uploaded_file, caption="Uploaded Card", use_container_width=True)

    # --- OCR STEP ---
    st.subheader("Extracted Text")
    st.write("Running OCR…")

    image = vision.Image(content=uploaded_file.getvalue())
    response = client.text_detection(image=image)
    texts = response.text_annotations

    if texts:
        st.text(texts[0].description)
    else:
        st.warning("No text detected.")
