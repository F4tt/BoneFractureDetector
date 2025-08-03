import streamlit as st
import requests
from PIL import Image
import io

st.title("Bone Fracture Detector")
API_URL = "http://127.0.0.1:7861/predict"

uploaded_file = st.file_uploader("Upload an X-ray image", type=["jpg","jpeg","png"])

if uploaded_file:
    img = Image.open(uploaded_file).convert("RGB")
    st.image(img, caption="Uploaded Image", use_column_width=True)

    with st.spinner("Detecting..."):
        response = requests.post(API_URL, files={"file": uploaded_file.getvalue()})
        if response.status_code == 200:
            result = response.json()
            st.json(result)
        else:
            st.error("Prediction failed!")
