FROM python:3.9-slim

WORKDIR /app

# ============================
# 1. Cài đặt system dependencies
# ============================
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgtk-3-0 \
    libgl1 \
    fontconfig \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ============================
# 2. Tạo thư mục cache writable
# ============================
ENV MPLCONFIGDIR=/app/.cache/matplotlib
ENV YOLO_CONFIG_DIR=/app/.cache/ultralytics
ENV STREAMLIT_CONFIG_DIR=/app/.streamlit
RUN mkdir -p /app/.cache/matplotlib \
    /app/.cache/ultralytics \
    /app/.streamlit \
    && chmod -R 777 /app/.cache /app/.streamlit

# ============================
# 3. Cài đặt Python dependencies
# ============================
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ============================
# 4. Copy code ứng dụng
# ============================
COPY . .

# ============================
# 5. Expose port & healthcheck
# ============================
EXPOSE 7860
HEALTHCHECK CMD curl --fail http://localhost:7860/_stcore/health || exit 1

# ============================
# 6. Run Streamlit app với XSRF off
# ============================
CMD ["streamlit", "run", "app.py", \
     "--server.port=7860", \
     "--server.address=0.0.0.0", \
     "--server.enableXsrfProtection=false"]
