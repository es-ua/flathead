# FLATHEAD Streaming Service

Unified audio/video streaming service for the Flathead robot.

## Features

- **4x INMP441 I2S Microphones**: Stereo front + stereo side for sound localization
- **2x Pi Camera v3**: Stereo vision on pan/tilt head
- **WebSocket streaming**: Low-latency real-time streaming
- **Docker containerized**: Easy deployment
- **Sound localization**: Calculate direction of sounds
- **Stereo depth**: Estimate distances from camera pair

## Quick Start

### On the Robot (Raspberry Pi 5)

```bash
# Clone and enter directory
cd /home/user/flathead/src/streaming

# Build and run with Docker
docker-compose up -d

# Or run directly
pip install -r requirements.txt
python main.py
```

### On Your PC/Server

```bash
# Run the receiving server
cd server
pip install websockets numpy opencv-python
python server.py

# Server will listen on ws://0.0.0.0:8765
```

## Configuration

Environment variables:

```bash
# Server connection
STREAM_WS_URL=ws://192.168.1.100:8765
STREAM_PROTOCOL=websocket  # or http

# Robot identification
ROBOT_ID=flathead-01

# Audio settings
AUDIO_ENABLED=true
AUDIO_SAMPLE_RATE=48000

# Video settings
VIDEO_ENABLED=true
VIDEO_WIDTH=640
VIDEO_HEIGHT=480
VIDEO_FPS=30

# Logging
LOG_LEVEL=INFO
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    RASPBERRY PI 5                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐    ┌─────────────┐                    │
│  │  I2S Bus 0  │    │  I2S Bus 1  │                    │
│  │  (Mics 1,2) │    │  (Mics 3,4) │                    │
│  └──────┬──────┘    └──────┬──────┘                    │
│         │                  │                            │
│         └────────┬─────────┘                            │
│                  │                                      │
│         ┌────────▼────────┐                            │
│         │  AudioStreamer  │                            │
│         └────────┬────────┘                            │
│                  │                                      │
│  ┌───────────────┼───────────────┐                     │
│  │               │               │                     │
│  │    ┌──────────▼──────────┐    │                     │
│  │    │  StreamingService   │    │                     │
│  │    └──────────┬──────────┘    │                     │
│  │               │               │                     │
│  └───────────────┼───────────────┘                     │
│                  │                                      │
│         ┌────────▼────────┐                            │
│         │ VideoStreamer   │                            │
│         └────────┬────────┘                            │
│                  │                                      │
│         ┌───────┴───────┐                              │
│         │               │                              │
│  ┌──────▼──────┐ ┌──────▼──────┐                      │
│  │  Camera L   │ │  Camera R   │                      │
│  │  (CSI 0)    │ │  (CSI 1)    │                      │
│  └─────────────┘ └─────────────┘                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
                         │
                         │ WebSocket
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                    SERVER / PC                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│         ┌─────────────────────┐                        │
│         │  StreamingServer    │                        │
│         │  (server.py)        │                        │
│         └──────────┬──────────┘                        │
│                    │                                    │
│         ┌──────────┼──────────┐                        │
│         │          │          │                        │
│         ▼          ▼          ▼                        │
│    ┌─────────┐ ┌─────────┐ ┌─────────┐                │
│    │ Display │ │ Record  │ │   AI    │                │
│    │ Video   │ │ Audio   │ │ Process │                │
│    └─────────┘ └─────────┘ └─────────┘                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Message Protocol

Binary message format:

```
┌──────────┬───────────┬────────────┬──────────┬──────────┐
│ msg_type │ source_id │ timestamp  │  length  │   data   │
│ (1 byte) │ (1 byte)  │ (8 bytes)  │ (4 bytes)│ (N bytes)│
└──────────┴───────────┴────────────┴──────────┴──────────┘

Message types:
  0x01 = Audio frame
  0x02 = Video frame
  0x03 = Stereo pair
  0xFF = Control message

Source IDs:
  Audio: 0=front, 1=side
  Video: 0=left, 1=right
```

## Hardware Setup

### I2S Microphones (INMP441)

```
Mic 1 (Front Left)  → I2S Bus 0, L/R=GND
Mic 2 (Front Right) → I2S Bus 0, L/R=3.3V
Mic 3 (Side Left)   → I2S Bus 1, L/R=GND
Mic 4 (Side Right)  → I2S Bus 1, L/R=3.3V
```

Enable I2S in `/boot/firmware/config.txt`:
```
dtparam=i2s=on
dtoverlay=googlevoicehat-soundcard
```

### Pi Cameras

```
Camera Left  → CAM0 connector
Camera Right → CAM1 connector
```

Both cameras mounted on 2-DOF pan/tilt head with ~7cm baseline.

## API Usage

### Python Client

```python
from streaming import StreamingService, StreamingConfig

config = StreamingConfig.from_env()
service = StreamingService(config)

# Start streaming
await service.run()
```

### Sound Localization

```python
from streaming import AudioStreamer, SoundLocalizer

audio = AudioStreamer(config.audio)
localizer = SoundLocalizer(mic_distance_cm=30)

# Get direction of sound
angle, confidence = localizer.calculate_direction(
    left_audio, right_audio, sample_rate=48000
)
print(f"Sound from {angle:.1f}° (confidence: {confidence:.2f})")
```

### Depth Estimation

```python
from streaming import StereoVideoStreamer, DepthEstimator

video = StereoVideoStreamer(config.video)
depth_estimator = DepthEstimator(baseline_cm=7.0)

# Get stereo frame
stereo = await video.get_stereo_frame()

# Compute depth map
disparity = depth_estimator.compute_disparity(
    stereo["left"].data,
    stereo["right"].data
)
depth_map = depth_estimator.disparity_to_depth(disparity)
```

## Docker Commands

```bash
# Build
docker-compose build

# Run in foreground
docker-compose up

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Run with test server
docker-compose --profile test up
```

## Troubleshooting

### No audio devices found

```bash
# Check I2S is enabled
cat /proc/device-tree/soc/i2s@*/status

# List audio devices
arecord -l

# Test recording
arecord -D plughw:0 -f S32_LE -r 48000 -c 2 -d 5 test.wav
```

### Cameras not detected

```bash
# Check camera connections
libcamera-hello --list-cameras

# Test capture
libcamera-still -o test.jpg
```

### WebSocket connection failed

```bash
# Check server is reachable
ping 192.168.1.100

# Test WebSocket
python -c "import websockets; print('OK')"

# Check firewall
sudo ufw allow 8765
```

## Performance

Typical resource usage on Pi 5:

```
CPU:      15-25% (video encoding)
Memory:   150-250 MB
Network:  2-5 Mbps (depends on video quality)
```

Latency:
- Audio: ~20ms (chunk size dependent)
- Video: ~50-100ms (encoding + network)

## License

MIT License - Part of Flathead Robot Project
