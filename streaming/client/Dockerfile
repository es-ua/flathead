# Raspberry Pi 5 Camera Streaming Client
FROM python:3.11-slim-bookworm

WORKDIR /app

# Install system dependencies for picamera2 and OpenCV
RUN apt-get update && apt-get install -y \
    libcamera-dev \
    libcamera-apps \
    python3-libcamera \
    python3-picamera2 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    ffmpeg \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./

# Create config directory
RUN mkdir -p /app/config

# Environment variables
ENV SERVER_URL=http://host.docker.internal:8080
ENV LEFT_CAMERA_ID=0
ENV RIGHT_CAMERA_ID=1
ENV PYTHONUNBUFFERED=1

# Run the client
CMD ["python", "main.py"]
