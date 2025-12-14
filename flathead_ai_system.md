# FLATHEAD ROBOT AI SYSTEM

## Technical Architecture Documentation

**RAG + LangGraph + LiveKit Integration**

Version 1.1 — December 2024

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Hardware Architecture](#2-hardware-architecture)
3. [RAG System Design](#3-rag-system-design)
4. [LangGraph Brain Architecture](#4-langgraph-brain-architecture)
5. [LiveKit Voice Integration](#5-livekit-voice-integration)
6. [Visual Activation System](#6-visual-activation-system)
7. [Sleep Mode & LED Indicators](#7-sleep-mode--led-indicators)
8. [Multi-Modal Interaction](#8-multi-modal-interaction)
9. [Docker Deployment](#9-docker-deployment)
10. [API Reference](#10-api-reference)

---

## 1. System Overview

### 1.1 Project Description

Flathead is an advanced home assistant robot inspired by Cyberpunk 2077, featuring multi-modal interaction capabilities including voice recognition, visual awareness, and intelligent conversation through RAG-enhanced language models.

### 1.2 Key Features

- Voice activation with speaker identification
- Visual activation through eye contact detection
- RAG-powered family knowledge base
- Multi-agent orchestration via LangGraph
- Real-time audio/video streaming via LiveKit
- Smart home integration
- Autonomous navigation with SLAM
- Sleep mode with LED status indication

### 1.3 Hybrid Architecture

The system operates in a hybrid mode with computation distributed between the robot (Raspberry Pi 5) and a home server (Mac Studio M4 Max):

| Component | Robot (Pi 5) | Server (Mac Studio) |
|-----------|--------------|---------------------|
| Sensors | Data capture | — |
| Vision (YOLO) | 20 FPS fallback | 60+ FPS CoreML |
| LLM | Llama 3B (500ms) | Llama 3B (50ms) |
| RAG | Cache only | Full Supabase |
| Voice Pipeline | Audio capture | STT/TTS/LangGraph |

### 1.4 Operating Modes

```
┌─────────────────────────────────────────────────────────────┐
│                    FLATHEAD ROBOT                           │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐   │
│  │         RASPBERRY PI 5 8GB (Core)                    │   │
│  │  - Coordination & routing                            │   │
│  │  - Local LLM (Llama 3.2 3B) - offline fallback      │   │
│  │  - Vision processing (YOLOv8)                        │   │
│  │  - SLAM (Hector)                                     │   │
│  │  - Audio (Whisper + Piper)                          │   │
│  └─────────────────────────────────────────────────────┘   │
│         ↓ Tailscale VPN ↓                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │      MAC STUDIO M4 MAX (Server)                      │   │
│  │  - Fast LLM inference (Metal optimized)             │   │
│  │  - Claude API orchestration                          │   │
│  │  - Accelerated vision (CoreML)                       │   │
│  │  - LiveKit server                                    │   │
│  │  - Supabase (RAG + state)                           │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

**Three Operating Modes:**

1. **HOME MODE (95%)** — WiFi 5-10ms to Mac Studio, full performance
2. **MOBILE MODE (4%)** — Tailscale VPN + 4G, ~50MB/hour
3. **OFFLINE MODE (1%)** — Pi 5 only, local LLM, basic autonomy

---

## 2. Hardware Architecture

### 2.1 Robot Components (Raspberry Pi 5 8GB)

#### Vision System
- 2× OV5647 cameras (stereo configuration)
- Baseline: 10-12 cm
- Resolution: 640×480 (depth), up to 1920×1080
- FOV: 66° diagonal each
- Depth range: 0.5m - 5m accurate
- FPS: 20-30 (Pi), 60+ (Mac)

#### Navigation System
- RPLIDAR A1M8 (12m range, 8000 samples/s)
- IMU BNO055 (9-axis, 100Hz)
- GPS u-blox SAM-M10Q (±5m outdoor)
- Wheel encoders JGA25-370

#### Audio System
- 4× INMP441 I2S MEMS microphones
- Circular array layout (360° coverage)
- Sound localization: GCC-PHAT TDOA (±15-20°)
- Speaker for TTS output

#### Locomotion
- 12× MG996R servos (spider legs)
- 4× DC motors with encoders (wheels)
- Hybrid movement capability

### 2.2 Server Components (Mac Studio M4 Max)

- Neural Engine 16-core for ML inference
- Unified Memory up to 128GB
- Metal Performance Shaders optimization
- Always-on, low power consumption (~30-40W)

### 2.3 Network Configuration

Connection between robot and server via Tailscale VPN:

- **Home Mode:** WiFi, 5-10ms latency
- **Mobile Mode:** 4G hotspot, 20-50ms latency
- **Offline Mode:** Pi-only operation

---

## 3. RAG System Design

### 3.1 Why Supabase/pgvector

For a home robot with family data, Supabase (PostgreSQL + pgvector) offers significant advantages over dedicated vector databases like Qdrant:

- **Expected data volume:** ~100k documents over 5 years (well within pgvector limits)
- **Single database** for vectors, metadata, history, and state
- **SQL joins** for complex queries ("what did wife say about vacation last week")
- **Row Level Security** for family privacy
- **Realtime subscriptions** for instant sync
- **Built-in auth, storage, and edge functions**

### 3.2 Knowledge Collections

| Collection | Description |
|------------|-------------|
| `home.layout` | Room layouts, furniture positions, navigation waypoints |
| `home.objects` | Object locations (keys, remotes, documents) |
| `home.devices` | Smart home devices, manuals, API endpoints |
| `family.*` | Personal profiles, preferences, schedules per family member |
| `work.*` | Projects, contacts, notes (private to owner) |
| `routines.*` | Morning/evening rituals, weekly schedules |
| `history.*` | Conversation logs, events, decisions |

### 3.3 Database Schema

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE knowledge (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    embedding VECTOR(768),  -- nomic-embed-text
    collection TEXT NOT NULL,
    owner TEXT DEFAULT 'shared',
    visibility TEXT DEFAULT 'family',
    confidence FLOAT DEFAULT 1.0,
    tags TEXT[],
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- HNSW index for fast similarity search
CREATE INDEX knowledge_embedding_idx
ON knowledge USING hnsw (embedding vector_cosine_ops);

-- Additional indexes
CREATE INDEX knowledge_collection_idx ON knowledge(collection);
CREATE INDEX knowledge_owner_idx ON knowledge(owner);
CREATE INDEX knowledge_tags_idx ON knowledge USING gin(tags);
```

### 3.4 Chunking Strategies

| Data Type | Strategy | Size |
|-----------|----------|------|
| Facts about family | 1 fact = 1 chunk | 50-100 tokens |
| Instructions | By steps | 100-200 tokens |
| Conversations | By exchange | 200-300 tokens |
| Documents | Semantic split | 300-500 tokens |

### 3.5 Retrieval Pipeline

```python
async def retrieve(query: str, user: str, context: dict) -> list[dict]:
    # 1. Generate query embedding
    query_embedding = await get_embedding(query)
    
    # 2. Determine collections by intent
    collections = detect_collections(query)
    
    # 3. Contextual filters
    filters = build_filters(
        user=user,
        collections=collections,
        location=context.get('robot_location'),
        time_range=extract_time_range(query)
    )
    
    # 4. Hybrid search (vector + full-text)
    results = await db.fetch("""
        SELECT *,
            (1 - (embedding <=> $1)) * 0.7 +
            ts_rank(fts, plainto_tsquery('russian', $2)) * 0.3 
            AS score
        FROM knowledge
        WHERE collection = ANY($3)
          AND (owner = $4 OR owner = 'shared' OR visibility = 'family')
        ORDER BY score DESC
        LIMIT 5
    """, query_embedding, query, collections, user)
    
    # 5. Rerank by recency and confidence
    return rerank_results(results)
```

---

## 4. LangGraph Brain Architecture

### 4.1 Why LangGraph

LangGraph provides state machine capabilities for complex AI agent orchestration:

- Conditional routing based on intent classification
- Parallel execution of independent agents
- Human-in-the-loop for critical actions
- Persistent state across conversation turns
- Interrupt handling for urgent events

### 4.2 State Definition

```python
@dataclass
class FlatheadState:
    # Input
    user_input: str = ""
    speaker_id: str = "unknown"
    input_type: str = "voice"  # voice, text, visual
    
    # Context
    conversation_history: list = field(default_factory=list)
    robot_location: dict = field(default_factory=dict)
    robot_battery: int = 100
    sensor_data: dict = field(default_factory=dict)
    
    # Power state
    power_state: PowerState = PowerState.LISTENING
    vision_enabled: bool = True
    
    # Processing
    intents: list = field(default_factory=list)
    rag_results: list = field(default_factory=list)
    actions_to_execute: list = field(default_factory=list)
    
    # Output
    response_text: str = ""
    response_actions: list = field(default_factory=list)
```

### 4.3 Agent Pool

| Agent | Triggers | Actions |
|-------|----------|---------|
| RAG Agent | question, find_object, recall | Search knowledge base |
| Task Agent | create_task, reminder, schedule | Create reminders, manage tasks |
| Nav Agent | navigate, go_to, follow | Path planning, movement |
| Home Agent | control_device, turn_on/off | Smart home control |
| Chat Agent | smalltalk, greeting | Casual conversation |

### 4.4 Graph Structure

```
Entry → Router → [Intent Classification]
                        │
        ┌───────────────┼───────────────┐
        ↓               ↓               ↓
   RAG Agent      Task Agent      Action Agent
        │               │               │
        └───────────────┼───────────────┘
                        ↓
               Response Generator
                        ↓
                       END
```

### 4.5 Conditional Routing

```python
def route_by_intent(state: FlatheadState) -> list[str]:
    """Determine which agents are needed"""
    
    # Skip visual processing in sleep mode
    if state.input_type == 'visual' and not state.vision_enabled:
        return []
    
    routes = []
    for intent in state.intents:
        match intent["type"]:
            case "find_object" | "question":
                routes.append("rag_agent")
            case "create_reminder" | "create_task":
                routes.append("task_agent")
            case "go_to" | "navigate":
                routes.append("nav_agent")
            case "control_device":
                routes.append("home_agent")
            case "smalltalk":
                routes.append("chat_agent")
    
    return list(set(routes))
```

---

## 5. LiveKit Voice Integration

### 5.1 Architecture Overview

LiveKit provides the real-time communication layer:

- WebRTC-based audio/video streaming
- Voice Activity Detection (VAD) via Silero
- Speech-to-Text via Whisper
- Text-to-Speech via Piper
- Speaker identification for family members
- Interruptible conversation support

### 5.2 Voice Pipeline

```
4× Mic Array → VAD → Beamforming → AEC
                                    ↓
                           LiveKit Audio Track
                                    ↓
┌──────────────────────────────────────────────────┐
│           LiveKit Server (Mac Studio)            │
│                                                  │
│  Audio → Whisper → LangGraph Brain → Piper → Out │
└──────────────────────────────────────────────────┘
```

### 5.3 LangGraph-LiveKit Adapter

```python
class LangGraphLLMAdapter(lk_llm.LLM):
    def __init__(self, brain: FlatheadBrain):
        self.brain = brain
    
    async def chat(self, history, temperature, n):
        # Extract user message from LiveKit history
        user_message = get_last_user_message(history)
        
        # Create LangGraph state
        state = FlatheadState(
            user_input=user_message,
            speaker_id=self.current_speaker,
            robot_location=await get_robot_state()
        )
        
        # Process through LangGraph
        result = await self.brain.process(state)
        
        # Execute actions asynchronously
        if result.response_actions:
            asyncio.create_task(execute_actions(result))
        
        # Return response to LiveKit
        return LLMResponse(result.response_text)
```

### 5.4 Speaker Identification

Family members are identified by voice embeddings stored in the database. On first interaction, the system prompts for identification; subsequent interactions use voice matching with a confidence threshold.

```python
class SpeakerIdentifier:
    def __init__(self, db: Database):
        self.db = db
        self.embeddings_cache = {}
    
    async def identify(self, audio_embedding: list[float]) -> str:
        # Compare against known family members
        results = await self.db.fetch("""
            SELECT name, 1 - (embedding <=> $1::vector) as similarity
            FROM family_voices
            ORDER BY similarity DESC
            LIMIT 1
        """, audio_embedding)
        
        if results and results[0]['similarity'] > 0.85:
            return results[0]['name']
        return "unknown"
```

---

## 6. Visual Activation System

### 6.1 Activation Triggers

The robot activates not only on voice commands but also through visual cues:

| Trigger | Detection Method | Response |
|---------|------------------|----------|
| Voice command | VAD + wake word | Process speech |
| Eye contact | Gaze estimation | "Yes? Can I help?" |
| Approach | Person tracking + depth | Turn toward person |
| Gesture | Pose estimation | Acknowledge + await |

### 6.2 Eye Contact Detection

Eye contact detection uses a multi-stage pipeline:

```python
# Stage 1: Face Detection (MediaPipe/YOLO-Face)
faces = face_detector.detect(frame)

# Stage 2: Facial Landmarks (468 points)
landmarks = face_mesh.process(face_roi)

# Stage 3: Eye Region Extraction
left_eye = extract_eye_region(landmarks, 'left')
right_eye = extract_eye_region(landmarks, 'right')

# Stage 4: Gaze Vector Estimation
gaze_vector = gaze_estimator.predict(left_eye, right_eye)

# Stage 5: Attention Check
is_looking = check_gaze_at_camera(gaze_vector, threshold=15°)
```

### 6.3 Attention State Machine

```python
class AttentionState(Enum):
    IDLE = 'idle'              # No one nearby
    DETECTED = 'detected'      # Person detected
    APPROACHING = 'approaching' # Person moving closer
    ATTENTION = 'attention'    # Eye contact established
    ENGAGED = 'engaged'        # In conversation
    LEAVING = 'leaving'        # Person moving away
```

**State Transitions:**

- `IDLE → DETECTED`: Person enters field of view
- `DETECTED → APPROACHING`: Distance decreasing for >1s
- `APPROACHING → ATTENTION`: Eye contact held for >0.5s
- `ATTENTION → ENGAGED`: Voice activity or continued attention
- `ENGAGED → LEAVING`: No interaction for >30s

### 6.4 Ambient Light Detection via Cameras

Instead of a separate light sensor, the stereo cameras determine ambient lighting:

```python
class AmbientLightDetector:
    def __init__(self):
        self.brightness_history = deque(maxlen=30)  # 1 second at 30fps
    
    def get_brightness(self, frame: np.ndarray) -> float:
        """Calculate average brightness from camera frame"""
        # Convert to grayscale and get mean
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return np.mean(gray) / 255.0  # Normalize to 0-1
    
    def get_lighting_condition(self, frame: np.ndarray) -> str:
        brightness = self.get_brightness(frame)
        self.brightness_history.append(brightness)
        avg_brightness = np.mean(self.brightness_history)
        
        if avg_brightness < 0.1:
            return 'dark'       # Night / lights off
        elif avg_brightness < 0.3:
            return 'dim'        # Evening / low light
        elif avg_brightness < 0.7:
            return 'normal'     # Normal indoor
        else:
            return 'bright'     # Daylight / bright lights
    
    def should_auto_sleep(self, frame: np.ndarray) -> bool:
        """Suggest sleep mode if lights are off"""
        condition = self.get_lighting_condition(frame)
        return condition == 'dark'
```

### 6.5 Visual Activation Implementation

```python
class VisualActivationSystem:
    def __init__(self):
        self.face_detector = MediaPipeFaceDetector()
        self.gaze_estimator = GazeEstimator()
        self.person_tracker = PersonTracker()
        self.light_detector = AmbientLightDetector()
        self.state = AttentionState.IDLE
        self.attention_start = None
    
    async def process_frame(self, frame, depth_map) -> Optional[ActivationEvent]:
        # Check lighting conditions
        lighting = self.light_detector.get_lighting_condition(frame)
        
        # Detect and track people
        people = self.person_tracker.update(frame, depth_map)
        
        if not people:
            self.state = AttentionState.IDLE
            return None
        
        # Find closest person
        closest = min(people, key=lambda p: p.distance)
        
        # Check for eye contact
        if closest.face_visible:
            gaze = self.gaze_estimator.estimate(closest.face)
            is_looking = gaze.is_at_camera(threshold=15)
            
            if is_looking:
                if self.state != AttentionState.ATTENTION:
                    self.attention_start = time.time()
                    self.state = AttentionState.ATTENTION
                
                # Sustained attention triggers activation
                if time.time() - self.attention_start > 0.5:
                    return ActivationEvent(
                        type='visual_attention',
                        person_id=closest.id,
                        distance=closest.distance,
                        confidence=gaze.confidence,
                        lighting=lighting
                    )
        
        return None
```

### 6.6 Integration with LangGraph

```python
async def on_visual_activation(event: ActivationEvent):
    # Identify the person
    person = await identify_person(event.person_id)
    
    # Create state for LangGraph
    state = FlatheadState(
        user_input='[VISUAL_ACTIVATION]',
        input_type='visual',
        speaker_id=person.name if person else 'unknown',
        sensor_data={
            'activation_type': 'eye_contact',
            'person_distance': event.distance,
            'confidence': event.confidence,
            'lighting': event.lighting
        }
    )
    
    # Process through brain
    result = await brain.process(state)
    
    # Speak greeting
    if person:
        await speak(f'Hi {person.name}! What can I do for you?')
    else:
        await speak('Hello! How can I help?')
```

### 6.7 Gesture Recognition (Future)

Planned gesture support:

- **Wave:** Attract attention from distance
- **Come here:** Robot approaches user
- **Stop:** Halt current action
- **Point:** Direct robot's attention
- **Thumbs up/down:** Confirm or reject

---

## 7. Sleep Mode & LED Indicators

### 7.1 Power States Overview

| State | LED Pattern | Active Systems | Power Draw |
|-------|-------------|----------------|------------|
| ACTIVE | Solid cyan | Voice + Vision + Nav | ~21W |
| LISTENING | Pulsing blue | Voice + Vision | ~14W |
| SLEEP | Slow breathing amber | Voice only | ~7W |
| DEEP_SLEEP | Off (blink every 5s) | Wake word only | ~3W |
| CHARGING | Pulsing green | Voice only | ~5W + charge |
| ERROR | Flashing red | Diagnostics | Variable |

### 7.2 LED Hardware Configuration

The status LED is an RGB NeoPixel (WS2812B) positioned in the robot's 'eye' area:

```python
# LED Pin Configuration (GPIO)
LED_PIN = 18  # PWM-capable pin
LED_COUNT = 2  # Stereo 'eyes' effect
LED_BRIGHTNESS = 0.3  # 30% for indoor use

class LEDColor:
    CYAN = (0, 255, 255)      # Active/Engaged
    BLUE = (0, 100, 255)      # Listening
    AMBER = (255, 150, 0)     # Sleep
    GREEN = (0, 255, 0)       # Charging
    RED = (255, 0, 0)         # Error
    WHITE = (255, 255, 255)   # Processing
    PURPLE = (150, 0, 255)    # Thinking/RAG query
    OFF = (0, 0, 0)           # Deep sleep
```

### 7.3 Power State Machine

```python
class PowerState(Enum):
    ACTIVE = 'active'           # Full awareness
    LISTENING = 'listening'     # Awaiting input
    SLEEP = 'sleep'             # Voice-only mode
    DEEP_SLEEP = 'deep_sleep'   # Wake word only
    CHARGING = 'charging'       # On charging dock
    ERROR = 'error'             # System error
```

**State Transitions:**

| From → To | Trigger | Condition |
|-----------|---------|-----------|
| LISTENING → ACTIVE | Voice/Visual | User interaction detected |
| ACTIVE → LISTENING | Timeout | No interaction for 30s |
| LISTENING → SLEEP | Timeout/Command | No interaction for 5min OR "go to sleep" |
| SLEEP → LISTENING | Voice only | Wake word OR direct speech |
| SLEEP → DEEP_SLEEP | Schedule/Battery | Night hours (23:00-06:00) OR battery <15% |
| DEEP_SLEEP → SLEEP | Wake word | "Hey Flathead" OR morning schedule |
| ANY → CHARGING | Dock detected | Charging voltage detected |
| ANY → SLEEP | Light | Cameras detect darkness for >5min |

### 7.4 Implementation

```python
class PowerStateManager:
    def __init__(self):
        self.state = PowerState.LISTENING
        self.led = LEDController()
        self.light_detector = AmbientLightDetector()
        self.last_interaction = time.time()
        self.vision_enabled = True
        
        # Timeouts (seconds)
        self.ACTIVE_TIMEOUT = 30
        self.LISTENING_TIMEOUT = 300  # 5 min
        self.DARK_TIMEOUT = 300       # 5 min of darkness
        
        # Night mode schedule
        self.NIGHT_START = 23  # 23:00
        self.NIGHT_END = 6     # 06:00
    
    async def transition_to(self, new_state: PowerState):
        old_state = self.state
        self.state = new_state
        
        # Update LED
        await self.led.set_state(new_state)
        
        # Enable/disable vision based on state
        if new_state in [PowerState.SLEEP, PowerState.DEEP_SLEEP]:
            self.vision_enabled = False
            await self.disable_vision_processing()
        else:
            self.vision_enabled = True
            await self.enable_vision_processing()
        
        # Announce state change
        if new_state == PowerState.SLEEP:
            await self.speak('Going to sleep. Say my name to wake me.')
        elif new_state == PowerState.LISTENING and old_state == PowerState.SLEEP:
            await self.speak('I am awake.')
    
    async def check_auto_sleep(self, frame: np.ndarray):
        """Check if should auto-sleep based on lighting"""
        if self.light_detector.should_auto_sleep(frame):
            if not hasattr(self, '_dark_start'):
                self._dark_start = time.time()
            elif time.time() - self._dark_start > self.DARK_TIMEOUT:
                await self.transition_to(PowerState.SLEEP)
        else:
            self._dark_start = None
    
    async def on_voice_activity(self, text: str, speaker: str):
        """Handle voice input in any state"""
        self.last_interaction = time.time()
        
        # Check for sleep command
        if self._is_sleep_command(text):
            await self.transition_to(PowerState.SLEEP)
            return
        
        # Wake from sleep/deep_sleep
        if self.state in [PowerState.SLEEP, PowerState.DEEP_SLEEP]:
            await self.transition_to(PowerState.ACTIVE)
        elif self.state == PowerState.LISTENING:
            await self.transition_to(PowerState.ACTIVE)
        
        return await self.process_input(text, speaker)
    
    async def on_visual_activation(self, event):
        """Handle visual input only if vision is enabled"""
        if not self.vision_enabled:
            return None  # Ignore in sleep mode
        
        self.last_interaction = time.time()
        
        if self.state == PowerState.LISTENING:
            await self.transition_to(PowerState.ACTIVE)
        
        return await self.process_visual(event)
    
    def _is_sleep_command(self, text: str) -> bool:
        sleep_phrases = [
            'go to sleep', 'засыпай', 'спи',
            'goodnight', 'sleep mode', 'спать'
        ]
        return any(p in text.lower() for p in sleep_phrases)
```

### 7.5 LED Controller

```python
class LEDController:
    def __init__(self):
        self.pixels = neopixel.NeoPixel(
            board.D18, 2, brightness=0.3, auto_write=False
        )
        self._animation_task = None
    
    async def set_state(self, state: PowerState):
        # Cancel current animation
        if self._animation_task:
            self._animation_task.cancel()
        
        match state:
            case PowerState.ACTIVE:
                self._set_solid(LEDColor.CYAN)
            
            case PowerState.LISTENING:
                self._animation_task = asyncio.create_task(
                    self._pulse(LEDColor.BLUE, speed=1.0)
                )
            
            case PowerState.SLEEP:
                self._animation_task = asyncio.create_task(
                    self._breathe(LEDColor.AMBER, speed=0.3)
                )
            
            case PowerState.DEEP_SLEEP:
                self._animation_task = asyncio.create_task(
                    self._slow_blink(LEDColor.AMBER, interval=5.0)
                )
            
            case PowerState.CHARGING:
                self._animation_task = asyncio.create_task(
                    self._pulse(LEDColor.GREEN, speed=0.5)
                )
            
            case PowerState.ERROR:
                self._animation_task = asyncio.create_task(
                    self._flash(LEDColor.RED, speed=2.0)
                )
    
    async def _breathe(self, color, speed=0.3):
        """Slow breathing effect for sleep mode"""
        while True:
            # Fade in
            for i in range(0, 100, 2):
                brightness = i / 100
                self._set_color_brightness(color, brightness)
                await asyncio.sleep(speed / 50)
            # Fade out
            for i in range(100, 0, -2):
                brightness = i / 100
                self._set_color_brightness(color, brightness)
                await asyncio.sleep(speed / 50)
            # Pause at bottom
            await asyncio.sleep(1.0)
    
    async def _slow_blink(self, color, interval=5.0):
        """Single brief blink every N seconds for deep sleep"""
        while True:
            self._set_solid(color)
            await asyncio.sleep(0.1)
            self._set_solid(LEDColor.OFF)
            await asyncio.sleep(interval)
```

### 7.6 Voice-Only Wake Detection

In SLEEP and DEEP_SLEEP modes, vision is disabled but audio remains active:

```python
class SleepModeAudioProcessor:
    def __init__(self):
        self.wake_words = ['flathead', 'флэтхед', 'hey flathead']
        self.vad = silero.VAD()
        self.wake_detector = WakeWordDetector(self.wake_words)
    
    async def process_audio_sleep_mode(self, audio_frame):
        """Lightweight audio processing for sleep mode"""
        
        # Stage 1: Voice Activity Detection (very cheap)
        if not self.vad.is_speech(audio_frame):
            return None
        
        # Stage 2: Wake word detection (medium cost)
        wake_detected = await self.wake_detector.check(audio_frame)
        
        if wake_detected:
            return WakeEvent(confidence=wake_detected.confidence)
        
        # Stage 3: Direct speech detection (full STT)
        if self._is_loud_directed_speech(audio_frame):
            text = await self.transcribe(audio_frame)
            if self._seems_directed_at_robot(text):
                return WakeEvent(confidence=0.8, transcription=text)
        
        return None
```

---

## 8. Multi-Modal Interaction

### 8.1 Unified Activation Handler

All activation modalities converge into a single handler:

```python
class UnifiedActivationHandler:
    def __init__(self):
        self.voice_system = VoiceActivationSystem()
        self.visual_system = VisualActivationSystem()
        self.power_manager = PowerStateManager()
        self.current_interaction = None
        self.priority_queue = asyncio.PriorityQueue()
    
    async def run(self):
        await asyncio.gather(
            self._voice_loop(),
            self._visual_loop(),
            self._power_state_loop(),
            self._process_activations()
        )
    
    async def _process_activations(self):
        while True:
            priority, activation = await self.priority_queue.get()
            
            # Check power state for visual activations
            if activation.type == 'visual':
                if not self.power_manager.vision_enabled:
                    continue  # Skip in sleep mode
            
            # Voice has priority over visual
            if self.current_interaction:
                if activation.type == 'voice':
                    await self._handle_activation(activation)
            else:
                await self._handle_activation(activation)
```

### 8.2 Context Preservation

When switching between modalities, context is preserved:

- Visual activation captures the person's identity
- Subsequent voice input is attributed to that person
- RAG queries filter by speaker context
- Response personalization based on known preferences

### 8.3 Proactive Interaction

The robot can initiate interactions based on observations:

```python
async def on_person_detected(person, context):
    if person.name == 'unknown':
        await notify_owner('Unknown person detected')
        return
    
    # Check for pending reminders
    reminders = await get_pending_reminders(person.name)
    if reminders:
        await approach_and_remind(person, reminders[0])
    
    # Time-based greetings
    if is_morning() and not person.greeted_today:
        await speak(f'Good morning, {person.name}!')
        await deliver_morning_briefing(person)
```

---

## 9. Docker Deployment

### 9.1 Docker Compose (Mac Studio)

```yaml
version: '3.8'

services:
  supabase-db:
    image: supabase/postgres:15.1.1.78
    ports:
      - '5432:5432'
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - supabase_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    command: >
      postgres 
      -c shared_preload_libraries='pg_stat_statements,pgvector'

  livekit:
    image: livekit/livekit-server:latest
    ports:
      - '7880:7880'
      - '7881:7881'
    environment:
      - LIVEKIT_KEYS=devkey:secret
    command: --config /etc/livekit.yaml
    volumes:
      - ./livekit.yaml:/etc/livekit.yaml

  ollama:
    image: ollama/ollama:latest
    ports:
      - '11434:11434'
    volumes:
      - ollama_data:/root/.ollama

  flathead-brain:
    build: ./brain
    ports:
      - '8100:8100'
    environment:
      - DATABASE_URL=postgresql://postgres:${POSTGRES_PASSWORD}@supabase-db:5432/flathead
      - OLLAMA_URL=http://ollama:11434
      - LIVEKIT_URL=ws://livekit:7880
      - LIVEKIT_API_KEY=devkey
      - LIVEKIT_API_SECRET=secret
    depends_on:
      - supabase-db
      - ollama
      - livekit

volumes:
  supabase_data:
  ollama_data:
```

### 9.2 Python Dependencies

```txt
# Core
langgraph==0.2.0
langchain==0.3.0
langchain-anthropic==0.2.0

# LiveKit
livekit==0.11.0
livekit-agents==0.8.0
livekit-plugins-silero==0.6.0

# Vision
opencv-python==4.8.1
ultralytics==8.0.200
mediapipe==0.10.9

# Database
asyncpg==0.29.0

# Audio
faster-whisper==0.9.0
piper-tts==1.2.0

# LED Control
adafruit-circuitpython-neopixel==6.3.0
rpi-gpio==0.7.1

# Utils
httpx==0.25.0
redis==5.0.1
paho-mqtt==1.6.1
```

---

## 10. API Reference

### 10.1 RAG Service Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/query` | RAG query with retrieval + generation |
| POST | `/ingest` | Add new knowledge to database |
| GET | `/sync/critical` | Get critical knowledge for offline cache |
| POST | `/state/update` | Update robot state in database |

### 10.2 LangGraph Brain Events

| Event | Payload |
|-------|---------|
| `voice_activation` | `{text, speaker_id, confidence}` |
| `visual_activation` | `{person_id, distance, gaze_confidence}` |
| `action_complete` | `{action_type, success, details}` |
| `power_state_change` | `{old_state, new_state, reason}` |
| `emergency` | `{type, location, severity}` |

### 10.3 Visual System Metrics

| Metric | Pi 5 (Fallback) | Mac Studio |
|--------|-----------------|------------|
| Face detection | 15-20 FPS | 60+ FPS |
| Gaze estimation | 10-15 FPS | 30+ FPS |
| Person tracking | 20-25 FPS | 60+ FPS |
| Activation latency | ~200ms | ~50ms |
| Light detection | 30 FPS | 60 FPS |

---

## Appendix: Quick Start

### A.1 Initial Setup

1. Deploy Docker stack on Mac Studio
2. Configure Tailscale VPN on both devices
3. Initialize Supabase database with schema
4. Pull Ollama models (`llama3.2:3b`, `nomic-embed-text`)
5. Calibrate stereo cameras
6. Register family voice profiles
7. Populate initial knowledge base
8. Configure LED pins on Pi 5

### A.2 Testing Checklist

- [ ] Voice activation responds within 500ms
- [ ] Eye contact triggers greeting within 1s
- [ ] RAG retrieves relevant family knowledge
- [ ] Speaker identification accuracy >90%
- [ ] Navigation to charging station works
- [ ] Smart home commands execute correctly
- [ ] Sleep mode disables vision processing
- [ ] LED correctly reflects power state
- [ ] Wake word works in sleep mode
- [ ] Auto-sleep triggers in darkness

### A.3 Voice Commands

| Command | Action |
|---------|--------|
| "Hey Flathead" | Wake from any sleep state |
| "Go to sleep" / "Засыпай" | Enter sleep mode |
| "Where are my keys?" | RAG search for objects |
| "Remind [person] to [task]" | Create reminder |
| "Go to the kitchen" | Navigate to location |
| "Turn on the lights" | Smart home control |

---

*End of Document*
