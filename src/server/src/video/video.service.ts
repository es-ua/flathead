import { Injectable, Logger } from '@nestjs/common';
import * as fs from 'fs';
import * as path from 'path';

export interface VideoFrame {
  robotId: string;
  cameraId: number; // 0=left, 1=right
  timestamp: number;
  data: Buffer; // JPEG encoded
}

@Injectable()
export class VideoService {
  private readonly logger = new Logger(VideoService.name);
  private readonly snapshotsDir = './recordings/snapshots';
  private readonly videosDir = './recordings/videos';

  // Latest frames for each robot/camera
  private latestFrames: Map<string, Buffer> = new Map();

  constructor() {
    // Ensure directories exist
    [this.snapshotsDir, this.videosDir].forEach((dir) => {
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
    });
  }

  processFrame(robotId: string, cameraId: number, data: Buffer): void {
    const cameraName = cameraId === 0 ? 'left' : 'right';
    const key = `${robotId}_${cameraName}`;

    // Store latest frame
    this.latestFrames.set(key, data);

    // Here you could add:
    // - Object detection
    // - Face detection
    // - Motion detection
    // - Stereo depth estimation
  }

  getLatestFrame(robotId: string, cameraId: number): Buffer | null {
    const cameraName = cameraId === 0 ? 'left' : 'right';
    const key = `${robotId}_${cameraName}`;
    return this.latestFrames.get(key) || null;
  }

  getStereoFrames(robotId: string): { left: Buffer; right: Buffer } | null {
    const left = this.latestFrames.get(`${robotId}_left`);
    const right = this.latestFrames.get(`${robotId}_right`);

    if (!left || !right) return null;

    return { left, right };
  }

  saveSnapshot(robotId: string, cameraId: number): string | null {
    const frame = this.getLatestFrame(robotId, cameraId);
    if (!frame) return null;

    const cameraName = cameraId === 0 ? 'left' : 'right';
    const filename = `${robotId}_${cameraName}_${Date.now()}.jpg`;
    const filepath = path.join(this.snapshotsDir, filename);

    fs.writeFileSync(filepath, frame);
    this.logger.log(`Saved snapshot: ${filepath}`);

    return filepath;
  }

  saveStereoSnapshot(robotId: string): { left: string; right: string } | null {
    const stereo = this.getStereoFrames(robotId);
    if (!stereo) return null;

    const timestamp = Date.now();

    const leftPath = path.join(
      this.snapshotsDir,
      `${robotId}_left_${timestamp}.jpg`,
    );
    const rightPath = path.join(
      this.snapshotsDir,
      `${robotId}_right_${timestamp}.jpg`,
    );

    fs.writeFileSync(leftPath, stereo.left);
    fs.writeFileSync(rightPath, stereo.right);

    this.logger.log(`Saved stereo snapshot: ${leftPath}, ${rightPath}`);

    return { left: leftPath, right: rightPath };
  }
}
