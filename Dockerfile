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
ENV HOME=/home/appuser

# 3. Add local bin to PATH (important for Streamlit)
ENV PATH=$HOME/.local/bin:$PATH

# 4. Writable cache directories
ENV MPLCONFIGDIR=$HOME/.cache/matplotlib
ENV YOLO_CONFIG_DIR=$HOME/.cache/ultralytics
RUN mkdir -p $MPLCONFIGDIR $YOLO_CONFIG_DIR

# 5. Install Python dependencies
COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# 6. Copy app code
COPY --chown=appuser:appuser . .

EXPOSE 7860

# 7. Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
