FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy code first (để giữ cache hiệu quả)
COPY requirements.txt ./

# Install system dependencies & Python deps
RUN apt-get update && apt-get install -y \
    libgl1 libglib2.0-0 git \
    && rm -rf /var/lib/apt/lists/* \
    && python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy rest of the code
COPY . .

# Streamlit config dir (fix permission issue)
ENV STREAMLIT_HOME=/app/.streamlit
RUN mkdir -p /app/.streamlit

# Make entrypoint executable
RUN chmod +x app.sh

# Expose FastAPI port
EXPOSE 7860
# Optional: expose Streamlit port for debugging
EXPOSE 7861

# Run entrypoint
CMD ["./app.sh"]
