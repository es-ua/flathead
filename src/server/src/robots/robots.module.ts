import { Module } from '@nestjs/common';
import { RobotsController } from './robots.controller';
import { RobotsService } from './robots.service';
import { StreamingModule } from '../streaming/streaming.module';

@Module({
  imports: [StreamingModule],
  controllers: [RobotsController],
  providers: [RobotsService],
})
export class RobotsModule {}
