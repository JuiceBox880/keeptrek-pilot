import streamlit as st

st.set_page_config(page_title="KeepTrek Pilot", layout="centered")

st.title("🏕️ KeepTrek Pilot")
st.write("Upload a guest or info card to begin.")

uploaded_file = st.file_uploader(
    "Upload an info card image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    st.success("Card received.")
    st.image(uploaded_file, caption="Uploaded Card", use_container_width=True)
