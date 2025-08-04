import cv2
import numpy as np
from ultralytics import YOLO
from PIL import Image
import streamlit as st

class BoneFractureDetector:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        
    def detect_fractures(self, image):
        """
        Phát hiện gãy xương trong ảnh
        """
        results = self.model(image)
        return results
    
    def draw_bounding_boxes(self, image, results):
        """
        Vẽ bounding box lên ảnh
        """
        # Convert PIL to OpenCV format
        img_array = np.array(image)
        img_cv2 = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # Lấy tọa độ bounding box
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = box.conf[0].cpu().numpy()
                    class_id = int(box.cls[0].cpu().numpy())
                    
                    # Vẽ rectangle
                    cv2.rectangle(img_cv2, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                    
                    # Thêm label
                    label = f"Fracture: {confidence:.2f}"
                    cv2.putText(img_cv2, label, (int(x1), int(y1) - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Convert back to PIL
        img_rgb = cv2.cvtColor(img_cv2, cv2.COLOR_BGR2RGB)
        return Image.fromarray(img_rgb)
    
    def get_detection_summary(self, results):
        """
        Tạo tóm tắt kết quả detection
        """
        total_fractures = 0
        high_confidence_fractures = 0
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                total_fractures += len(boxes)
                for box in boxes:
                    confidence = box.conf[0].cpu().numpy()
                    if confidence > 0.7:
                        high_confidence_fractures += 1
        
        return {
            "total_fractures": total_fractures,
            "high_confidence_fractures": high_confidence_fractures
        }