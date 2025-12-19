import { Injectable, Logger } from '@nestjs/common';
import * as fs from 'fs';
import * as path from 'path';

export interface AudioFrame {
  robotId: string;
  sourceId: number; // 0=front, 1=side
  timestamp: number;
  data: Buffer;
}

@Injectable()
export class AudioService {
  private readonly logger = new Logger(AudioService.name);
  private readonly recordingsDir = './recordings/audio';
  private recording = false;
  private recordingBuffers: Map<string, Buffer[]> = new Map();

  constructor() {
    // Ensure recordings directory exists
    if (!fs.existsSync(this.recordingsDir)) {
      fs.mkdirSync(this.recordingsDir, { recursive: true });
    }
  }

  processFrame(robotId: string, sourceId: number, data: Buffer): void {
    // Update stats, process audio, etc.
    const sourceName = sourceId === 0 ? 'front' : 'side';

    // If recording, buffer the data
    if (this.recording) {
      const key = `${robotId}_${sourceName}`;
      if (!this.recordingBuffers.has(key)) {
        this.recordingBuffers.set(key, []);
      }
      this.recordingBuffers.get(key).push(data);
    }

    // Here you could add:
    // - Voice activity detection
    // - Speech-to-text
    // - Sound classification
    // - Sound localization
  }

  startRecording(): void {
    this.recording = true;
    this.recordingBuffers.clear();
    this.logger.log('Started recording audio');
  }

  stopRecording(): string[] {
    this.recording = false;
    const savedFiles: string[] = [];

    // Save all buffered audio
    this.recordingBuffers.forEach((buffers, key) => {
      const combined = Buffer.concat(buffers);
      const filename = `${key}_${Date.now()}.raw`;
      const filepath = path.join(this.recordingsDir, filename);

      fs.writeFileSync(filepath, combined);
      savedFiles.push(filepath);
      this.logger.log(`Saved audio: ${filepath}`);
    });

    this.recordingBuffers.clear();
    return savedFiles;
  }

  // Get audio level (RMS) from buffer
  getAudioLevel(data: Buffer): number {
    // Assuming 32-bit signed integer samples
    let sum = 0;
    const samples = data.length / 4;

    for (let i = 0; i < data.length; i += 4) {
      const sample = data.readInt32LE(i);
      sum += sample * sample;
    }

    const rms = Math.sqrt(sum / samples);
    // Normalize to 0-1 range (assuming 24-bit audio in 32-bit container)
    return rms / 0x7fffff;
  }
}
