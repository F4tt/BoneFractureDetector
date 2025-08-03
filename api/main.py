from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from ultralytics import YOLO
from io import BytesIO
from PIL import Image
import cv2
import numpy as np
import os

app = FastAPI(title="Bone Fracture Detector API")

MODEL_PATH = os.path.join(os.path.dirname(__file__), "best.pt")
model = YOLO(MODEL_PATH)

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # Read image
    img_bytes = await file.read()
    img = Image.open(BytesIO(img_bytes)).convert("RGB")

    # Inference
    results = model.predict(img)

    # Draw bounding boxes
    plotted_img = results[0].plot()  # numpy array BGR
    plotted_img = cv2.cvtColor(plotted_img, cv2.COLOR_BGR2RGB)

    # Convert to BytesIO for response
    pil_img = Image.fromarray(plotted_img)
    buf = BytesIO()
    pil_img.save(buf, format="JPEG")
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/jpeg")
