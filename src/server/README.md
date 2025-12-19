# FLATHEAD Streaming Server

NestJS server for receiving audio/video streams from Flathead robot.

## Features

- **WebSocket Gateway**: Real-time streaming with Socket.IO
- **REST API**: Robot management, snapshots, recordings
- **Web UI**: Browser-based stream viewer
- **Multi-robot**: Support for multiple robots simultaneously
- **Recording**: Save audio and video snapshots
- **Swagger Docs**: Auto-generated API documentation

## Quick Start

### With Docker (Recommended)

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Server available at:
#   HTTP API:    http://localhost:3000
#   WebSocket:   ws://localhost:3000
#   Swagger:     http://localhost:3000/api
```

### With Docker + Web UI

```bash
# Run with web viewer
docker-compose --profile ui up -d

# Open in browser:
#   http://localhost:8080
```

### Local Development

```bash
# Install dependencies
npm install

# Start in development mode
npm run start:dev

# Build for production
npm run build
npm run start:prod
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     NestJS Server                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐     ┌─────────────────┐               │
│  │ StreamingGateway│     │ RobotsController│               │
│  │   (WebSocket)   │     │    (REST API)   │               │
│  └────────┬────────┘     └────────┬────────┘               │
│           │                       │                         │
│           └───────────┬───────────┘                         │
│                       │                                     │
│           ┌───────────┴───────────┐                         │
│           │   StreamingService    │                         │
│           └───────────┬───────────┘                         │
│                       │                                     │
│           ┌───────────┴───────────┐                         │
│           │                       │                         │
│   ┌───────▼───────┐       ┌───────▼───────┐                │
│   │ AudioService  │       │ VideoService  │                │
│   └───────────────┘       └───────────────┘                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## WebSocket Events

### From Robot

```javascript
// Register robot
socket.emit('robot:hello', {
  robotId: 'flathead-01',
  capabilities: {
    audio: true,
    video: true,
    audioChannels: 4,
    videoChannels: 2
  }
});

// Stream audio frame
socket.emit('audio:frame', binaryData);

// Stream video frame
socket.emit('video:frame', binaryData);
```

### From Viewer

```javascript
// Join as viewer
socket.emit('viewer:join', { robotId: 'flathead-01' }, (response) => {
  console.log('Connected robots:', response.robots);
});

// Receive video frame
socket.on('video:frame', (data) => {
  const img = document.getElementById('video');
  img.src = 'data:image/jpeg;base64,' + data.data;
});

// Receive audio frame
socket.on('audio:frame', (data) => {
  // Process audio data
});

// Robot connected/disconnected
socket.on('robot:connected', (data) => { ... });
socket.on('robot:disconnected', (data) => { ... });
```

### Send Command to Robot

```javascript
socket.emit('robot:command', {
  robotId: 'flathead-01',
  command: 'move',
  params: { direction: 'forward', speed: 0.5 }
});
```

## REST API

### Robots

```bash
# Get all connected robots
GET /robots

# Get specific robot
GET /robots/:robotId

# Get streaming stats
GET /robots/:robotId/stats

# Get camera snapshot (returns JPEG)
GET /robots/:robotId/snapshot/left
GET /robots/:robotId/snapshot/right

# Save stereo snapshot
POST /robots/:robotId/snapshot

# Start/stop audio recording
POST /robots/:robotId/recording/start
POST /robots/:robotId/recording/stop
```

### Swagger Documentation

Visit `http://localhost:3000/api` for interactive API docs.

## Configuration

Environment variables:

```bash
# Server
PORT=3000
NODE_ENV=production

# CORS
CORS_ORIGIN=*
```

## Binary Protocol

Messages from robot use this binary format:

```
┌──────────┬───────────┬────────────┬──────────┬──────────┐
│ msg_type │ source_id │ timestamp  │  length  │   data   │
│ (1 byte) │ (1 byte)  │ (8 bytes)  │ (4 bytes)│ (N bytes)│
└──────────┴───────────┴────────────┴──────────┴──────────┘

Message types:
  0x01 = Audio
  0x02 = Video
  0xFF = Control

Source IDs:
  Audio: 0=front mics, 1=side mics
  Video: 0=left camera, 1=right camera
```

## File Storage

Recordings are saved to:

```
recordings/
├── audio/          # Audio recordings (.raw)
├── snapshots/      # Camera snapshots (.jpg)
└── videos/         # Video recordings
```

## Development

```bash
# Watch mode
npm run start:dev

# Debug mode (attach debugger to port 9229)
npm run start:debug

# Lint
npm run lint

# Format
npm run format

# Test
npm run test
```

## Docker Commands

```bash
# Build
docker-compose build

# Run production
docker-compose up -d

# Run with web UI
docker-compose --profile ui up -d

# Run development mode
docker-compose --profile dev up

# View logs
docker-compose logs -f server

# Stop
docker-compose down

# Clean up
docker-compose down -v --rmi all
```

## Example: Python Robot Client

```python
import socketio

sio = socketio.Client()

@sio.event
def connect():
    print('Connected to server')
    sio.emit('robot:hello', {
        'robotId': 'flathead-01',
        'capabilities': {
            'audio': True,
            'video': True,
            'audioChannels': 4,
            'videoChannels': 2
        }
    })

@sio.event
def command(data):
    print(f"Received command: {data}")
    # Handle command from viewer

sio.connect('http://localhost:3000')

# Send video frame
sio.emit('video:frame', frame_bytes)

# Send audio frame
sio.emit('audio:frame', audio_bytes)
```

## License

MIT License - Part of Flathead Robot Project
