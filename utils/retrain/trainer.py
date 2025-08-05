# utils/retrain/trainer.py
import os
from pathlib import Path
import json
from datetime import datetime
from huggingface_hub import HfApi, snapshot_download
from ultralytics import YOLO
from utils.retrain.config import (
    HF_DATASET_NAME, HF_DATASET_LOCAL_DIR,
    LAST_COMMIT_FILE, BASE_MODEL_PATH, BEST_MODEL_PATH,
    METRICS_LOG_FILE, EPOCHS, IMG_SIZE, BATCH_SIZE
)

class YOLOTrainer:
    def __init__(self):
        self.api = HfApi()

    def check_dataset_update(self, client_payload=None):
        """Check latest commit hash of HF dataset."""
        # Nếu webhook gửi payload chứa commit SHA mới, dùng luôn
        if client_payload and "commit" in client_payload:
            latest_commit = client_payload["commit"]
            print(f"Webhook payload commit: {latest_commit}")
        else:
            ds_info = self.api.dataset_info(HF_DATASET_NAME)
            latest_commit = ds_info.sha
            print(f"Fetched latest commit from HF: {latest_commit}")

        Path("data").mkdir(parents=True, exist_ok=True)
        old_commit = Path(LAST_COMMIT_FILE).read_text().strip() if Path(LAST_COMMIT_FILE).exists() else None

        Path(LAST_COMMIT_FILE).write_text(latest_commit)
        return latest_commit != old_commit

    def download_dataset(self):
        print("Downloading dataset from HF...")
        snapshot_download(
            repo_id=HF_DATASET_NAME,
            repo_type="dataset",
            local_dir=HF_DATASET_LOCAL_DIR,
            local_dir_use_symlinks=False
        )

    def train(self):
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
        metrics = model.val()
        new_metrics = {
            "timestamp": datetime.now().isoformat(),
            "mAP50": float(metrics.box.map50),
            "precision": float(metrics.box.mp),
            "recall": float(metrics.box.mr),
        }

        metrics_history = {"history": [], "best_metrics": None}
        if Path(METRICS_LOG_FILE).exists():
            metrics_history = json.loads(Path(METRICS_LOG_FILE).read_text())

        best_metrics = metrics_history.get("best_metrics")
        if not best_metrics or new_metrics["mAP50"] > best_metrics["mAP50"]:
            print("🎉 New model is better! Updating best model...")
            model.export(format="pt")
            os.replace("models/training_logs/last.pt", BEST_MODEL_PATH)
            metrics_history["best_metrics"] = new_metrics

        metrics_history["history"].append(new_metrics)
        Path(METRICS_LOG_FILE).write_text(json.dumps(metrics_history, indent=2))

    def run(self, force_retrain=False, client_payload=None):
        dataset_changed = self.check_dataset_update(client_payload)

        if not dataset_changed and not force_retrain:
            print("Dataset not updated. Skipping retrain.")
            return

        self.download_dataset()
        model, _ = self.train()
        self.evaluate_and_update(model)


if __name__ == "__main__":
    import json
    payload_str = os.getenv("CLIENT_PAYLOAD", "{}")
    client_payload = json.loads(payload_str)
    force = os.getenv("FORCE_RETRAIN", "false").lower() == "true"

    trainer = YOLOTrainer()
    trainer.run(force_retrain=force, client_payload=client_payload)
