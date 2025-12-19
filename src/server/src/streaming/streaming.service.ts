import { Injectable, Logger } from '@nestjs/common';
import { EventEmitter2 } from '@nestjs/event-emitter';

export interface StreamStats {
  robotId: string;
  audioFrames: number;
  videoFrames: number;
  bytesReceived: number;
  startTime: Date;
  lastFrameTime: Date;
}

@Injectable()
export class StreamingService {
  private readonly logger = new Logger(StreamingService.name);
  private stats: Map<string, StreamStats> = new Map();

  constructor() {}

  getStats(robotId: string): StreamStats | undefined {
    return this.stats.get(robotId);
  }

  getAllStats(): StreamStats[] {
    return Array.from(this.stats.values());
  }

  updateStats(
    robotId: string,
    type: 'audio' | 'video',
    bytesReceived: number,
  ): void {
    let stat = this.stats.get(robotId);

    if (!stat) {
      stat = {
        robotId,
        audioFrames: 0,
        videoFrames: 0,
        bytesReceived: 0,
        startTime: new Date(),
        lastFrameTime: new Date(),
      };
      this.stats.set(robotId, stat);
    }

    if (type === 'audio') {
      stat.audioFrames++;
    } else {
      stat.videoFrames++;
    }

    stat.bytesReceived += bytesReceived;
    stat.lastFrameTime = new Date();
  }

  clearStats(robotId: string): void {
    this.stats.delete(robotId);
  }
}
