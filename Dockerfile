FROM python:3.10-slim

WORKDIR /app

# Copy requirements trước để tận dụng cache
COPY requirements.txt .

# Install system & Python dependencies
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code
COPY . .

# Fix quyền ghi cho Streamlit và Matplotlib
ENV STREAMLIT_HOME=/app/.streamlit
ENV MPLCONFIGDIR=/app/.matplotlib
RUN mkdir -p $STREAMLIT_HOME $MPLCONFIGDIR

# Expose port 7860 cho Hugging Face
EXPOSE 7860

# Chạy Streamlit trực tiếp
CMD ["streamlit", "run", "scripts/ui.py", "--server.port=7860", "--server.address=0.0.0.0"]
