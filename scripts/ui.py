import streamlit as st
from ultralytics import YOLO
from PIL import Image
import cv2
import numpy as np
import torch,os

st.set_page_config(page_title="Bone Fracture Detector", layout="wide")
st.title("one Fracture Detector")

MODEL_PATH = os.path.join("api", "best.pt")

@st.cache_resource
def load_model():
    # Thêm safe load cho PyTorch 2.6+
    try:
        return YOLO(MODEL_PATH)
    except Exception as e:
        st.warning(f"Default load failed: {e}")
        ckpt = torch.load(MODEL_PATH, map_location="cpu", weights_only=False)
        model = YOLO()
        model.model = ckpt['model']
        return model

model = load_model()
