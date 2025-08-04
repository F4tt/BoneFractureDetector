FROM python:3.9-slim

WORKDIR /app

# 1. System dependencies
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

# 2. Writable cache dirs
ENV MPLCONFIGDIR=/app/.cache/matplotlib
ENV YOLO_CONFIG_DIR=/app/.cache/ultralytics
ENV XDG_CACHE_HOME=/app/.cache
RUN mkdir -p /app/.cache/matplotlib \
    /app/.cache/ultralytics \
    /app/.cache/fonts \
    && chmod -R 777 /app/.cache

# 3. Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy app code
COPY . .

# 5. Expose port & healthcheck
EXPOSE 7860
HEALTHCHECK CMD curl --fail http://localhost:7860/_stcore/health || exit 1

# 6. Run Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
