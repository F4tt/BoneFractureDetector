import streamlit as st
from PIL import Image
import os
from utils.detection import BoneFractureDetector

# Page config
st.set_page_config(
    page_title="Bone Fracture Detection",
    page_icon="🦴",
    layout="wide"
)

# Initialize model
@st.cache_resource
def load_model():
    model_path = "models/best.pt"
    if not os.path.exists(model_path):
        st.error("Model file not found! Please upload your .pt file to models/ directory.")
        return None
    return BoneFractureDetector(model_path)

def main():
    st.title("🦴 Bone Fracture Detection System")
    st.markdown("Upload an X-ray image to detect bone fractures using YOLO11")
    
    # Load model
    detector = load_model()
    if detector is None:
        return
    
    # Sidebar
    st.sidebar.header("Settings")
    confidence_threshold = st.sidebar.slider("Confidence Threshold", 0.1, 1.0, 0.5, 0.1)
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose an X-ray image...", 
        type=['png', 'jpg', 'jpeg'],
        help="Upload an X-ray image for fracture detection"
    )
    
    if uploaded_file is not None:
        # Display original image
        image = Image.open(uploaded_file)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Original Image")
            st.image(image, caption="Uploaded X-ray", use_column_width=True)
        
        with col2:
            st.subheader("Detection Results")
            
            # Run detection
            with st.spinner("Analyzing image..."):
                results = detector.detect_fractures(image)
                
                # Filter results by confidence threshold
                filtered_results = []
                for result in results:
                    if result.boxes is not None:
                        # Filter boxes by confidence
                        mask = result.boxes.conf >= confidence_threshold
                        if mask.any():
                            filtered_result = result
                            filtered_result.boxes = result.boxes[mask]
                            filtered_results.append(filtered_result)
                
                # Draw bounding boxes
                result_image = detector.draw_bounding_boxes(image, filtered_results)
                st.image(result_image, caption="Detected Fractures", use_column_width=True)
        
        # Display summary
        st.subheader("Detection Summary")
        summary = detector.get_detection_summary(filtered_results)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Fractures", summary["total_fractures"])
        with col2:
            st.metric("High Confidence (>0.7)", summary["high_confidence_fractures"])
        with col3:
            st.metric("Confidence Threshold", f"{confidence_threshold:.1f}")
        
        # Detailed results
        if summary["total_fractures"] > 0:
            st.subheader("Detailed Results")
            for i, result in enumerate(filtered_results):
                if result.boxes is not None:
                    for j, box in enumerate(result.boxes):
                        confidence = box.conf[0].cpu().numpy()
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        
                        st.write(f"**Fracture {j+1}:**")
                        st.write(f"- Confidence: {confidence:.3f}")
                        st.write(f"- Location: ({int(x1)}, {int(y1)}) to ({int(x2)}, {int(y2)})")
        else:
            st.info("No fractures detected with the current confidence threshold.")

if __name__ == "__main__":
    main()