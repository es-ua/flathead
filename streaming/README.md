# Flathead Video Streaming System

WebRTC-based video streaming from Raspberry Pi 5 to Mac Studio server.

## Architecture

```
┌─────────────────────────────────────┐
│       Raspberry Pi 5 (Client)       │
│  ┌────────────┐  ┌────────────┐     │
│  │ Pi Cam v3  │  │ Pi Cam v3  │     │
│  │   (left)   │  │  (right)   │     │
│  └─────┬──────┘  └─────┬──────┘     │
│        │               │            │
│        └───────┬───────┘            │
│                ▼                    │
│      ┌─────────────────┐            │
│      │ Python Client   │            │
│      │ (aiortc+picam2) │            │
│      └────────┬────────┘            │
└───────────────┼─────────────────────┘
                │ WebRTC (UDP)
                ▼
┌─────────────────────────────────────┐
│       Mac Studio (Server)           │
│      ┌─────────────────┐            │
│      │  NestJS Server  │            │
│      │ (wrtc+socket.io)│            │
│      └─────────────────┘            │
└─────────────────────────────────────┘
```

## Server (Mac Studio)

### Requirements
- Node.js 20+
- npm

### Setup
```bash
cd streaming/server
npm install
npm run build
npm run start:prod
```

### Development
```bash
npm run start:dev
```

### Docker
```bash
cd streaming/server
docker build -t flathead-server .
docker run -p 8080:8080 flathead-server
```

### Configuration
- `PORT`: Server port (default: 8080)

## Client (Raspberry Pi 5)

### Requirements
- Python 3.11+
- Pi Camera v3 modules (x2)
- picamera2 library

### Setup (without Docker)
```bash
cd streaming/client
pip install -r requirements.txt
python src/main.py
```

### Docker Setup
```bash
cd streaming/client

# Edit config
nano config/config.yml

# Set server URL
export SERVER_URL=http://192.168.1.100:8080

# Build and run
docker-compose up -d
```

### Configuration

Environment variables:
- `SERVER_URL`: WebRTC server URL (default: `http://localhost:8080`)
- `LEFT_CAMERA_ID`: Left camera device ID (default: `0`)
- `RIGHT_CAMERA_ID`: Right camera device ID (default: `1`)
- `CONFIG_PATH`: Path to config file

Config file (`config/config.yml`):
```yaml
server:
  url: "http://192.168.1.100:8080"
  namespace: "/stream"

cameras:
  left:
    device_id: 0
    width: 640
    height: 480
    fps: 30
  right:
    device_id: 1
    width: 640
    height: 480
    fps: 30
```

## API Events (Socket.IO)

### Client → Server
- `offer`: Send WebRTC offer
  ```json
  { "cameraId": "left", "offer": { "type": "offer", "sdp": "..." } }
  ```
- `ice-candidate`: Send ICE candidate
  ```json
  { "cameraId": "left", "candidate": { ... } }
  ```
- `disconnect-camera`: Stop camera stream
  ```json
  { "cameraId": "left" }
  ```
- `stats`: Request connection stats

### Server → Client
- `connected`: Connection acknowledged
- `answer`: WebRTC answer
  ```json
  { "cameraId": "left", "answer": { "type": "answer", "sdp": "..." } }
  ```
- `error`: Error message
- `stats`: Connection statistics

## Testing

### Without cameras (mock mode)
The client automatically uses mock cameras when `picamera2` is not available, generating test pattern frames.

### Verify connection
```bash
# On server
curl http://localhost:8080/

# Watch server logs
docker logs -f flathead-server

# Watch client logs
docker logs -f flathead-camera-client
```

## Troubleshooting

### Camera not detected
```bash
# Check video devices
ls -la /dev/video*

# Check camera detection
vcgencmd get_camera
```

### WebRTC connection fails
- Ensure UDP ports are not blocked
- Check STUN server connectivity
- Verify server URL is reachable from Pi

### High latency
- Reduce resolution in config
- Check network bandwidth
- Ensure hardware encoding is active
