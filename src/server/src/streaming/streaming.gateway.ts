import {
  WebSocketGateway,
  WebSocketServer,
  SubscribeMessage,
  OnGatewayConnection,
  OnGatewayDisconnect,
  OnGatewayInit,
  MessageBody,
  ConnectedSocket,
} from '@nestjs/websockets';
import { Logger } from '@nestjs/common';
import { Server, Socket } from 'socket.io';
import { StreamingService } from './streaming.service';
import { AudioService } from '../audio/audio.service';
import { VideoService } from '../video/video.service';

// Message types (must match robot client)
const MSG_AUDIO = 0x01;
const MSG_VIDEO = 0x02;
const MSG_STEREO = 0x03;
const MSG_CONTROL = 0xff;

interface RobotInfo {
  robotId: string;
  connectedAt: Date;
  capabilities: {
    audio: boolean;
    video: boolean;
    audioChannels: number;
    videoChannels: number;
  };
  stats: {
    audioFrames: number;
    videoFrames: number;
    bytesReceived: number;
  };
}

@WebSocketGateway({
  cors: {
    origin: '*',
  },
  transports: ['websocket', 'polling'],
})
export class StreamingGateway
  implements OnGatewayInit, OnGatewayConnection, OnGatewayDisconnect
{
  @WebSocketServer()
  server: Server;

  private readonly logger = new Logger(StreamingGateway.name);
  private robots: Map<string, RobotInfo> = new Map();
  private viewers: Set<string> = new Set();

  constructor(
    private readonly streamingService: StreamingService,
    private readonly audioService: AudioService,
    private readonly videoService: VideoService,
  ) {}

  afterInit(server: Server) {
    this.logger.log('WebSocket Gateway initialized');

    // Stats logging every 10 seconds
    setInterval(() => {
      this.logStats();
    }, 10000);
  }

  handleConnection(client: Socket) {
    this.logger.log(`Client connected: ${client.id}`);
  }

  handleDisconnect(client: Socket) {
    this.logger.log(`Client disconnected: ${client.id}`);

    // Remove from robots if it was a robot
    if (this.robots.has(client.id)) {
      const robot = this.robots.get(client.id);
      this.logger.log(`Robot disconnected: ${robot.robotId}`);
      this.robots.delete(client.id);

      // Notify viewers
      this.server.to('viewers').emit('robot:disconnected', {
        robotId: robot.robotId,
      });
    }

    // Remove from viewers
    this.viewers.delete(client.id);
  }

  // Robot registration
  @SubscribeMessage('robot:hello')
  handleRobotHello(
    @ConnectedSocket() client: Socket,
    @MessageBody()
    data: {
      robotId: string;
      capabilities: {
        audio: boolean;
        video: boolean;
        audioChannels: number;
        videoChannels: number;
      };
    },
  ) {
    this.logger.log(`Robot registered: ${data.robotId}`);

    const robotInfo: RobotInfo = {
      robotId: data.robotId,
      connectedAt: new Date(),
      capabilities: data.capabilities,
      stats: {
        audioFrames: 0,
        videoFrames: 0,
        bytesReceived: 0,
      },
    };

    this.robots.set(client.id, robotInfo);

    // Join robot room
    client.join(`robot:${data.robotId}`);

    // Notify viewers
    this.server.to('viewers').emit('robot:connected', {
      robotId: data.robotId,
      capabilities: data.capabilities,
    });

    return { status: 'ok', message: 'Robot registered' };
  }

  // Viewer registration
  @SubscribeMessage('viewer:join')
  handleViewerJoin(
    @ConnectedSocket() client: Socket,
    @MessageBody() data: { robotId?: string },
  ) {
    this.logger.log(`Viewer joined: ${client.id}`);
    this.viewers.add(client.id);
    client.join('viewers');

    // Subscribe to specific robot if requested
    if (data.robotId) {
      client.join(`robot:${data.robotId}:viewers`);
    }

    // Send list of connected robots
    const robotList = Array.from(this.robots.values()).map((r) => ({
      robotId: r.robotId,
      capabilities: r.capabilities,
      connectedAt: r.connectedAt,
    }));

    return { status: 'ok', robots: robotList };
  }

  // Binary audio stream from robot
  @SubscribeMessage('audio:frame')
  handleAudioFrame(
    @ConnectedSocket() client: Socket,
    @MessageBody() data: Buffer,
  ) {
    const robot = this.robots.get(client.id);
    if (!robot) return;

    robot.stats.audioFrames++;
    robot.stats.bytesReceived += data.length;

    // Parse header
    const parsed = this.parseFrame(data);
    if (!parsed) return;

    // Process audio
    this.audioService.processFrame(robot.robotId, parsed.sourceId, parsed.data);

    // Forward to viewers of this robot
    this.server.to(`robot:${robot.robotId}:viewers`).emit('audio:frame', {
      robotId: robot.robotId,
      sourceId: parsed.sourceId,
      timestamp: parsed.timestamp,
      data: parsed.data,
    });
  }

  // Binary video stream from robot
  @SubscribeMessage('video:frame')
  handleVideoFrame(
    @ConnectedSocket() client: Socket,
    @MessageBody() data: Buffer,
  ) {
    const robot = this.robots.get(client.id);
    if (!robot) return;

    robot.stats.videoFrames++;
    robot.stats.bytesReceived += data.length;

    // Parse header
    const parsed = this.parseFrame(data);
    if (!parsed) return;

    // Process video
    this.videoService.processFrame(robot.robotId, parsed.sourceId, parsed.data);

    // Forward to viewers (as base64 for browser compatibility)
    this.server.to(`robot:${robot.robotId}:viewers`).emit('video:frame', {
      robotId: robot.robotId,
      cameraId: parsed.sourceId,
      timestamp: parsed.timestamp,
      data: parsed.data.toString('base64'),
    });
  }

  // Raw binary message (for socket.io binary transport)
  @SubscribeMessage('stream:data')
  handleStreamData(
    @ConnectedSocket() client: Socket,
    @MessageBody() data: Buffer,
  ) {
    const robot = this.robots.get(client.id);
    if (!robot) return;

    // Parse message type from first byte
    if (data.length < 14) return;

    const msgType = data[0];

    if (msgType === MSG_AUDIO) {
      this.handleAudioFrame(client, data);
    } else if (msgType === MSG_VIDEO) {
      this.handleVideoFrame(client, data);
    }
  }

  // Control commands from viewers to robot
  @SubscribeMessage('robot:command')
  handleRobotCommand(
    @ConnectedSocket() client: Socket,
    @MessageBody() data: { robotId: string; command: string; params?: any },
  ) {
    this.logger.log(`Command for ${data.robotId}: ${data.command}`);

    // Forward to robot
    this.server.to(`robot:${data.robotId}`).emit('command', {
      command: data.command,
      params: data.params,
    });

    return { status: 'ok' };
  }

  // Get robot status
  @SubscribeMessage('robot:status')
  handleRobotStatus(
    @ConnectedSocket() client: Socket,
    @MessageBody() data: { robotId: string },
  ) {
    const robot = Array.from(this.robots.values()).find(
      (r) => r.robotId === data.robotId,
    );

    if (!robot) {
      return { status: 'error', message: 'Robot not found' };
    }

    return {
      status: 'ok',
      robot: {
        robotId: robot.robotId,
        connectedAt: robot.connectedAt,
        capabilities: robot.capabilities,
        stats: robot.stats,
      },
    };
  }

  // Parse binary frame with header
  private parseFrame(data: Buffer): {
    msgType: number;
    sourceId: number;
    timestamp: number;
    data: Buffer;
  } | null {
    if (data.length < 14) return null;

    const msgType = data.readUInt8(0);
    const sourceId = data.readUInt8(1);
    const timestamp = data.readDoubleBE(2);
    const length = data.readUInt32BE(10);

    if (data.length < 14 + length) return null;

    return {
      msgType,
      sourceId,
      timestamp,
      data: data.subarray(14, 14 + length),
    };
  }

  private logStats() {
    const totalRobots = this.robots.size;
    const totalViewers = this.viewers.size;

    let totalAudioFrames = 0;
    let totalVideoFrames = 0;
    let totalBytes = 0;

    this.robots.forEach((robot) => {
      totalAudioFrames += robot.stats.audioFrames;
      totalVideoFrames += robot.stats.videoFrames;
      totalBytes += robot.stats.bytesReceived;
    });

    if (totalRobots > 0) {
      this.logger.log(
        `Stats: ${totalRobots} robots, ${totalViewers} viewers, ` +
          `${totalAudioFrames} audio frames, ${totalVideoFrames} video frames, ` +
          `${(totalBytes / 1024 / 1024).toFixed(1)}MB received`,
      );
    }
  }
}
