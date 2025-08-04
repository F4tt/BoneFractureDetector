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

# 2. Create a non-root user
RUN useradd -m appuser
USER appuser

# 3. Set working directories for cache
ENV HOME=/home/appuser
ENV MPLCONFIGDIR=$HOME/.cache/matplotlib
ENV YOLO_CONFIG_DIR=$HOME/.cache/ultralytics
ENV STREAMLIT_CONFIG_DIR=$HOME/.streamlit

RUN mkdir -p $MPLCONFIGDIR $YOLO_CONFIG_DIR $STREAMLIT_CONFIG_DIR

# 4. Copy and install requirements
COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy app code
COPY --chown=appuser:appuser . .

EXPOSE 7860

# 6. Run Streamlit (user is non-root)
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
