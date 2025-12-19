import {
  Controller,
  Get,
  Post,
  Param,
  Res,
  HttpStatus,
  Query,
} from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiParam } from '@nestjs/swagger';
import { Response } from 'express';
import { RobotsService } from './robots.service';
import { StreamingService } from '../streaming/streaming.service';

@ApiTags('robots')
@Controller('robots')
export class RobotsController {
  constructor(
    private readonly robotsService: RobotsService,
    private readonly streamingService: StreamingService,
  ) {}

  @Get()
  @ApiOperation({ summary: 'Get all connected robots' })
  @ApiResponse({ status: 200, description: 'List of connected robots' })
  getAll() {
    return this.robotsService.getAllRobots();
  }

  @Get(':robotId')
  @ApiOperation({ summary: 'Get robot by ID' })
  @ApiParam({ name: 'robotId', description: 'Robot ID' })
  @ApiResponse({ status: 200, description: 'Robot details' })
  @ApiResponse({ status: 404, description: 'Robot not found' })
  getOne(@Param('robotId') robotId: string) {
    const robot = this.robotsService.getRobot(robotId);
    if (!robot) {
      return { error: 'Robot not found' };
    }
    return robot;
  }

  @Get(':robotId/stats')
  @ApiOperation({ summary: 'Get streaming stats for robot' })
  @ApiParam({ name: 'robotId', description: 'Robot ID' })
  getStats(@Param('robotId') robotId: string) {
    return this.streamingService.getStats(robotId);
  }

  @Get(':robotId/snapshot/:camera')
  @ApiOperation({ summary: 'Get latest camera snapshot' })
  @ApiParam({ name: 'robotId', description: 'Robot ID' })
  @ApiParam({ name: 'camera', description: 'Camera (left or right)' })
  async getSnapshot(
    @Param('robotId') robotId: string,
    @Param('camera') camera: string,
    @Res() res: Response,
  ) {
    const cameraId = camera === 'left' ? 0 : 1;
    const frame = this.robotsService.getLatestFrame(robotId, cameraId);

    if (!frame) {
      return res.status(HttpStatus.NOT_FOUND).json({ error: 'No frame available' });
    }

    res.setHeader('Content-Type', 'image/jpeg');
    res.send(frame);
  }

  @Post(':robotId/snapshot')
  @ApiOperation({ summary: 'Save stereo snapshot' })
  @ApiParam({ name: 'robotId', description: 'Robot ID' })
  saveSnapshot(@Param('robotId') robotId: string) {
    return this.robotsService.saveStereoSnapshot(robotId);
  }

  @Post(':robotId/recording/start')
  @ApiOperation({ summary: 'Start audio recording' })
  startRecording(@Param('robotId') robotId: string) {
    return this.robotsService.startRecording(robotId);
  }

  @Post(':robotId/recording/stop')
  @ApiOperation({ summary: 'Stop audio recording' })
  stopRecording(@Param('robotId') robotId: string) {
    return this.robotsService.stopRecording(robotId);
  }
}
