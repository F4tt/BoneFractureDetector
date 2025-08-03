from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse
from ultralytics import YOLO
from PIL import Image
import io

app = FastAPI()
model = YOLO("api/best.pt")

@app.post("/predict")
async def predict(file: UploadFile):
    image = Image.open(io.BytesIO(await file.read())).convert("RGB")
    results = model.predict(image)
    
    boxes = []
    for box in results[0].boxes:
        boxes.append({
            "x1": float(box.xyxy[0][0]),
            "y1": float(box.xyxy[0][1]),
            "x2": float(box.xyxy[0][2]),
            "y2": float(box.xyxy[0][3]),
            "conf": float(box.conf[0]),
            "cls": int(box.cls[0])
        })
    return JSONResponse(content={"boxes": boxes})
