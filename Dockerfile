FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y libglib2.0-0 libsm6 libxext6 \
   libxrender-dev libgomp1 libgtk-3-0 libgl1 fontconfig curl && rm -rf /var/lib/apt/lists/*

# Dùng non-root user hoặc tránh ghi vào /
ENV HF_HOME=/tmp
ENV MPLCONFIGDIR=/tmp/matplotlib_cache
ENV XDG_CACHE_HOME=/tmp

RUN mkdir -p /tmp/matplotlib_cache && chmod -R 777 /tmp/matplotlib_cache

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7860
CMD ["streamlit","run","app.py", "--server.port=7860", "--server.address=0.0.0.0","--server.enableXsrfProtection=false"]
