import os, shutil
from ultralytics import YOLO
from huggingface_hub import snapshot_download

DATASET_REPO = "F4t/X-Ray-Bone-Fracture-Detector-DTS"  # Update with your username
DATA_DIR = "Data/xray.v1.yolov11"
BEST_MODEL = "api/best.pt"
NEW_MODEL_PATH = "checkpoints/new_model.pt"
YOLO_PRETRAINED = "yolo11l.pt"  # Pretrained YOLOv11L

# 1. Download latest dataset
if os.path.exists(DATA_DIR):
    print("🧹 Remove old dataset to fetch latest...")
    shutil.rmtree(DATA_DIR)

print("Downloading latest dataset from Hugging Face...")
dataset_path = snapshot_download(repo_id=DATASET_REPO, repo_type="dataset")
print(f"Dataset ready at {dataset_path}")

# 2. Train new model
print("Training new model from YOLOv11 pretrained weights...")
model = YOLO(YOLO_PRETRAINED)
results = model.train(data=os.path.join(DATA_DIR, "data.yaml"), epochs=20, imgsz=640)
model.save(NEW_MODEL_PATH)

# 3. Evaluate new model
print("Evaluating new model...")
metrics = model.val()
new_map50 = metrics.box.map50
print(f"New model mAP50: {new_map50:.4f}")

# 4. Evaluate current best model
print("Evaluating current best model...")
best_model = YOLO(BEST_MODEL)
best_metrics = best_model.val()
best_map50 = best_metrics.box.map50
print(f"Current best mAP50: {best_map50:.4f}")

# 5. Compare and update
if new_map50 > best_map50:
    print("New model is better! Updating production best.pt...")
    shutil.copy(NEW_MODEL_PATH, BEST_MODEL)
else:
    print("New model is worse. Keeping current best.pt.")
