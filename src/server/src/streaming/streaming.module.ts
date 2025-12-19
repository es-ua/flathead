import { Module } from '@nestjs/common';
import { StreamingGateway } from './streaming.gateway';
import { StreamingService } from './streaming.service';
import { AudioService } from '../audio/audio.service';
import { VideoService } from '../video/video.service';

@Module({
  providers: [StreamingGateway, StreamingService, AudioService, VideoService],
  exports: [StreamingService],
})
export class StreamingModule {}
