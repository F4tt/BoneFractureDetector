import streamlit as st
from ultralytics import YOLO
from PIL import Image
import cv2
import numpy as np
import os

st.title("Bone Fracture Detector")

MODEL_PATH = os.path.join("api", "best.pt")
model = YOLO(MODEL_PATH)

uploaded_file = st.file_uploader("Upload an X-ray image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file).convert("RGB")
    st.image(img, caption="Uploaded Image", use_column_width=True)

    # Predict
    results = model.predict(img)
    plotted_img = results[0].plot()  # numpy array BGR
    plotted_img = cv2.cvtColor(plotted_img, cv2.COLOR_BGR2RGB)

    st.image(plotted_img, caption="Detection Result", use_column_width=True)
