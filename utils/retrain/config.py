# utils/retrain/config.py

# Hugging Face dataset
HF_DATASET_NAME = "F4t/X-Ray-Bone-Fracture-Detector-DTS"  # Sẽ được thay bằng secrets trong CI
HF_DATASET_LOCAL_DIR = "data"

# YOLO Training configs
EPOCHS = 50
IMG_SIZE = 640
BATCH_SIZE = 8

# Model paths
BASE_MODEL_PATH = "models/yolo11.pt"
BEST_MODEL_PATH = "models/best.pt"

# Log paths
METRICS_LOG_FILE = "models/training_logs/metrics_history.json"
LAST_COMMIT_FILE = "data/last_commit.txt"
