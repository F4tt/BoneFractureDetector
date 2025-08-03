FROM python:3.10-slim

# Set working dir
WORKDIR /app

# Copy code
COPY . .

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 libglib2.0-0 git \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

# Make entrypoint executable
RUN chmod +x app.sh

# Hugging Face Spaces expects Docker to run on port 7860
EXPOSE 7860

# Start app
CMD ["./app.sh"]
