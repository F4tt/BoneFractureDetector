import os
import shutil
from ultralytics import YOLO
from huggingface_hub import snapshot_download

# Config
DATASET_REPO = "F4t/X-Ray-Bone-Fracture-Detector-DTS"  # Hugging Face Dataset repo
DATA_DIR = "Data/xray.v1.yolov11"
BEST_MODEL = "api/best.pt"
CHECKPOINT_DIR = "checkpoints"
NEW_MODEL_PATH = os.path.join(CHECKPOINT_DIR, "new_model.pt")
YOLO_PRETRAINED = "yolo11l.pt"  # Pretrained YOLOv11L

os.makedirs(CHECKPOINT_DIR, exist_ok=True)

# 1. Download latest dataset
if os.path.exists(DATA_DIR):
    print("🧹 Remove old dataset to fetch latest...")
    shutil.rmtree(DATA_DIR)

print("📥 Downloading latest dataset from Hugging Face...")
dataset_cache = snapshot_download(repo_id=DATASET_REPO, repo_type="dataset")

# Copy dataset to project Data/
shutil.copytree(dataset_cache, DATA_DIR)
print(f"✅ Dataset ready at {DATA_DIR}")

data_yaml = os.path.join(DATA_DIR, "data.yaml")
if not os.path.exists(data_yaml):
    raise FileNotFoundError(f"data.yaml not found in {DATA_DIR}")

# 2. Train new model
print("🚀 Training new model from YOLOv11 pretrained weights...")
model = YOLO(YOLO_PRETRAINED)
results = model.train(data=data_yaml, epochs=20, imgsz=640)

# Lấy best.pt từ YOLO run
best_weight_path = os.path.join(model.trainer.save_dir, "weights", "best.pt")
if not os.path.exists(best_weight_path):
    raise FileNotFoundError("Best weight not found after training!")

shutil.copy(best_weight_path, NEW_MODEL_PATH)
print(f"✅ New model saved at {NEW_MODEL_PATH}")

# 3. Evaluate new model
print("📊 Evaluating new model...")
metrics = model.val(data=data_yaml)
new_map50 = metrics.box.map50
print(f"New model mAP50: {new_map50:.4f}")

# 4. Evaluate current best model
print("📊 Evaluating current best model...")
best_model = YOLO(BEST_MODEL)
best_metrics = best_model.val(data=data_yaml)
best_map50 = best_metrics.box.map50
print(f"Current best mAP50: {best_map50:.4f}")

# 5. Compare and update
if new_map50 > best_map50:
    print("🎉 New model is better! Updating production best.pt...")
    shutil.copy(NEW_MODEL_PATH, BEST_MODEL)
else:
    print("⚠️ New model is worse. Keeping current best.pt.")
