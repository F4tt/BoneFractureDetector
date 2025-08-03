FROM python:3.10-slim

WORKDIR /app

# Copy requirements trước để tận dụng cache
COPY requirements.txt .

# Install system & Python dependencies
RUN apt-get update && apt-get install -y \
    libgl1 libglib2.0-0 git \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code
COPY . .

# Fix quyền ghi cho Streamlit, Matplotlib và YOLO
ENV STREAMLIT_HOME=/app/.streamlit
ENV MPLCONFIGDIR=/app/.matplotlib
ENV YOLO_CONFIG_DIR=/app/.ultralytics
RUN mkdir -p $STREAMLIT_HOME $MPLCONFIGDIR $YOLO_CONFIG_DIR

# Expose port 7860 cho Hugging Face
EXPOSE 7860

# Chạy Streamlit trực tiếp
CMD ["streamlit", "run", "scripts/ui.py", "--server.port=7860", "--server.address=0.0.0.0"]
