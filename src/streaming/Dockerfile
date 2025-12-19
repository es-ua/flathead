# FLATHEAD Streaming Service
# For Raspberry Pi 5 with cameras and I2S microphones

FROM python:3.11-slim-bookworm

LABEL maintainer="Flathead Project"
LABEL description="Audio/Video streaming service for Flathead robot"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Audio
    libportaudio2 \
    portaudio19-dev \
    libasound2-dev \
    alsa-utils \
    # Video
    libopencv-dev \
    libcamera-dev \
    libcap-dev \
    # Build tools
    build-essential \
    pkg-config \
    # Cleanup
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first (for layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY *.py .

# Create non-root user
RUN useradd -m -s /bin/bash flathead && \
    usermod -aG audio,video flathead

# Set ownership
RUN chown -R flathead:flathead /app

# Switch to non-root user
USER flathead

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV STREAM_WS_URL=ws://192.168.1.100:8765
ENV ROBOT_ID=flathead-01
ENV AUDIO_ENABLED=true
ENV VIDEO_ENABLED=true
ENV LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import socket; socket.create_connection(('localhost', 8080), timeout=5)" || exit 1

# Run the service
CMD ["python", "main.py"]
