import { Injectable, Logger } from '@nestjs/common';
import { VideoService } from '../video/video.service';
import { AudioService } from '../audio/audio.service';

export interface Robot {
  robotId: string;
  connectedAt: Date;
  capabilities: {
    audio: boolean;
    video: boolean;
    audioChannels: number;
    videoChannels: number;
  };
  status: 'online' | 'offline';
}

@Injectable()
export class RobotsService {
  private readonly logger = new Logger(RobotsService.name);

  // This would be populated by the streaming gateway
  // For now, we'll use a simple in-memory store
  private robots: Map<string, Robot> = new Map();

  constructor(
    private readonly videoService: VideoService,
    private readonly audioService: AudioService,
  ) {}

  getAllRobots(): Robot[] {
    return Array.from(this.robots.values());
  }

  getRobot(robotId: string): Robot | undefined {
    return this.robots.get(robotId);
  }

  registerRobot(robot: Robot): void {
    this.robots.set(robot.robotId, robot);
    this.logger.log(`Robot registered: ${robot.robotId}`);
  }

  unregisterRobot(robotId: string): void {
    this.robots.delete(robotId);
    this.logger.log(`Robot unregistered: ${robotId}`);
  }

  getLatestFrame(robotId: string, cameraId: number): Buffer | null {
    return this.videoService.getLatestFrame(robotId, cameraId);
  }

  saveStereoSnapshot(
    robotId: string,
  ): { left: string; right: string } | { error: string } {
    const result = this.videoService.saveStereoSnapshot(robotId);
    if (!result) {
      return { error: 'No frames available' };
    }
    return result;
  }

  startRecording(robotId: string): { status: string } {
    this.audioService.startRecording();
    return { status: 'Recording started' };
  }

  stopRecording(robotId: string): { status: string; files: string[] } {
    const files = this.audioService.stopRecording();
    return { status: 'Recording stopped', files };
  }
}
