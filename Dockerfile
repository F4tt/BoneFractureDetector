FROM python:3.9-slim

WORKDIR /app

# ============================
# 1. System dependencies
# ============================
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgtk-3-0 \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*

# ============================
# 2. Create writable cache dirs
# ============================
ENV MPLCONFIGDIR=/app/.cache/matplotlib
ENV YOLO_CONFIG_DIR=/app/.cache/ultralytics
ENV FONTCONFIG_PATH=/etc/fonts
RUN mkdir -p /app/.cache/matplotlib && \
    mkdir -p /app/.cache/ultralytics && \
    chmod -R 777 /app/.cache

# ============================
# 3. Install Python deps
# ============================
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ============================
# 4. Copy app code
# ============================
COPY . .

EXPOSE 7860
HEALTHCHECK CMD curl --fail http://localhost:7860/_stcore/health

CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
