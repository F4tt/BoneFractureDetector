# utils/retrain/trainer.py

import os
from pathlib import Path
from huggingface_hub import HfApi, snapshot_download
import json
from datetime import datetime
from ultralytics import YOLO

from utils.retrain.config import (
    HF_DATASET_NAME, HF_DATASET_LOCAL_DIR,
    LAST_COMMIT_FILE, BASE_MODEL_PATH, BEST_MODEL_PATH,
    METRICS_LOG_FILE, EPOCHS, IMG_SIZE, BATCH_SIZE
)

class YOLOTrainer:
    def __init__(self):
        self.api = HfApi()

    def check_dataset_update(self):
        """Check latest commit hash of HF dataset."""
        ds_info = self.api.dataset_info(HF_DATASET_NAME)
        latest_commit = ds_info.sha

        Path("data").mkdir(parents=True, exist_ok=True)

        # Read old commit hash
        if Path(LAST_COMMIT_FILE).exists():
            old_commit = Path(LAST_COMMIT_FILE).read_text().strip()
        else:
            old_commit = None

        # Save new commit hash
        Path(LAST_COMMIT_FILE).write_text(latest_commit)

        # Return True if dataset changed
        return latest_commit != old_commit

    def download_dataset(self):
        """Download dataset snapshot from HF."""
        print("Downloading dataset from HF...")
        snapshot_download(
            repo_id=HF_DATASET_NAME,
            repo_type="dataset",
            local_dir=HF_DATASET_LOCAL_DIR,
            local_dir_use_symlinks=False
        )

    def train(self):
        """Train YOLO model"""
        print("Starting YOLO training...")
        model = YOLO(BASE_MODEL_PATH)
        results = model.train(
            data=f"{HF_DATASET_LOCAL_DIR}/data.yaml",
            epochs=EPOCHS,
            imgsz=IMG_SIZE,
            batch=BATCH_SIZE,
            project="models/training_logs",
            name=f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        return model, results

    def evaluate_and_update(self, model):
        """Evaluate new model and update best model if better"""
        metrics = model.val()
        new_metrics = {
            "timestamp": datetime.now().isoformat(),
            "mAP50": float(metrics.box.map50),
            "precision": float(metrics.box.mp),
            "recall": float(metrics.box.mr),
        }

        # Load metrics history
        metrics_history = {"history": [], "best_metrics": None}
        if Path(METRICS_LOG_FILE).exists():
            metrics_history = json.loads(Path(METRICS_LOG_FILE).read_text())

        # Compare with best model
        best_metrics = metrics_history.get("best_metrics")
        if not best_metrics or new_metrics["mAP50"] > best_metrics["mAP50"]:
            print("🎉 New model is better! Updating best model...")
            model.export(format="pt")  # save as last.pt
            os.replace("models/training_logs/last.pt", BEST_MODEL_PATH)
            metrics_history["best_metrics"] = new_metrics

        # Save metrics history
        metrics_history["history"].append(new_metrics)
        Path(METRICS_LOG_FILE).write_text(json.dumps(metrics_history, indent=2))

    def run(self, force_retrain=False):
        """Main pipeline"""
        dataset_changed = self.check_dataset_update()

        if not dataset_changed and not force_retrain:
            print("Dataset not updated. Skipping retrain.")
            return

        self.download_dataset()
        model, _ = self.train()
        self.evaluate_and_update(model)


if __name__ == "__main__":
    trainer = YOLOTrainer()
    # Force retrain can be passed via sys.argv or env var
    force = os.getenv("FORCE_RETRAIN", "false").lower() == "true"
    trainer.run(force_retrain=force)
