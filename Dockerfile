FROM python:3.10-slim

WORKDIR /app

# 1. Copy requirements trước để tận dụng cache
COPY requirements.txt ./

# 2. Install system dependencies & Python packages
RUN apt-get update && apt-get install -y \
    libgl1 libglib2.0-0 git \
    && rm -rf /var/lib/apt/lists/* \
    && python -m pip install --upgrade pip \
    && pip install --no-cache-dir torch==2.5.1 torchvision==0.20.1 \
    && pip install --no-cache-dir -r requirements.txt

# 3. Copy toàn bộ project
COPY . .

# 4. Fix permission cho Streamlit, Matplotlib và Ultralytics
ENV STREAMLIT_HOME=/app/.streamlit
ENV MPLCONFIGDIR=/app/.config/matplotlib
ENV YOLO_CONFIG_DIR=/app/.config/ultralytics

RUN mkdir -p $STREAMLIT_HOME $MPLCONFIGDIR $YOLO_CONFIG_DIR

# 5. Make entrypoint executable
RUN chmod +x app.sh

# Hugging Face Space chỉ public cổng 7860
EXPOSE 7860

CMD ["./app.sh"]
