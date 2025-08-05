import streamlit as st
from PIL import Image
import numpy as np
import os
from utils.detection import BoneFractureDetector

# =========================
# Page configuration
# =========================
st.set_page_config(
    page_title="Bone Fracture Detection",
    layout="wide",
)

MODEL_PATH = "models/best.pt"

# =========================
# Load model with caching
# =========================
@st.cache_resource
def load_model():
    if not os.path.exists(MODEL_PATH):
        st.error("Model file not found! Please upload `models/best.pt`.")
        return None
    return BoneFractureDetector(MODEL_PATH)

# =========================
# Main App
# =========================
def main():
    st.title("Bone Fracture Detection System")
    st.markdown("Upload an X-ray image to detect bone fractures")

    # Load model
    detector = load_model()
    if detector is None:
        return

    # Sidebar settings
    st.sidebar.header("⚙️ Settings")
    confidence_threshold = st.sidebar.slider(
        "Confidence Threshold", 0.1, 1.0, 0.5, 0.05
    )
    image_size = st.sidebar.select_slider(
        "Image Resize (NxN)",
        options=[640, 800, 1024],
        value=640,
    )

    # File uploader
    uploaded_file = st.file_uploader(
        "Upload an X-ray image...",
        type=["png", "jpg", "jpeg"],
        help="Upload an X-ray image for fracture detection"
    )

    if uploaded_file is not None:
        # Open and resize image
        original_image = Image.open(uploaded_file).convert("RGB")
        resized_image = original_image.resize((image_size, image_size))

        # Display original & detection results
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Original Image")
            st.image(original_image, caption=f"Original ({original_image.size[0]}x{original_image.size[1]})", use_container_width=True)

        with col2:
            st.subheader(f"Detection Results (Resized to {image_size}x{image_size})")
            with st.spinner("Analyzing image..."):
                # Run detection
                results = detector.detect_fractures(resized_image)

                # Filter detections by confidence
                filtered_results = []
                for result in results:
                    if result.boxes is not None:
                        mask = result.boxes.conf >= confidence_threshold
                        if mask.any():
                            filtered_result = result
                            filtered_result.boxes = result.boxes[mask]
                            filtered_results.append(filtered_result)

                # Draw bounding boxes
                result_image = detector.draw_bounding_boxes(resized_image.copy(), filtered_results)
                st.image(result_image, caption="Detected Fractures", use_container_width=True)

        # Detection summary
        st.subheader("Detection Summary")
        summary = detector.get_detection_summary(filtered_results)

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Fractures", summary["total_fractures"])
        col2.metric("High Confidence (>0.7)", summary["high_confidence_fractures"])
        col3.metric("Confidence Threshold", f"{confidence_threshold:.2f}")

        # Detailed results
        if summary["total_fractures"] > 0:
            st.subheader("Detailed Results")
            for i, result in enumerate(filtered_results):
                if result.boxes is not None:
                    for j, box in enumerate(result.boxes):
                        conf = float(box.conf[0])
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        st.write(
                            f"**Fracture {j+1}:** Confidence {conf:.3f}, "
                            f"Box [{x1}, {y1}] → [{x2}, {y2}]"
                        )
        else:
            st.info("No fractures detected with the current confidence threshold.")


if __name__ == "__main__":
    main()
