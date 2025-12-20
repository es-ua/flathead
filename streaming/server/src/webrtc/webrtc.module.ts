import { Module } from '@nestjs/common';
import { WebrtcGateway } from './webrtc.gateway';
import { WebrtcService } from './webrtc.service';
import { StreamModule } from '../stream/stream.module';

@Module({
  imports: [StreamModule],
  providers: [WebrtcGateway, WebrtcService],
  exports: [WebrtcService],
})
export class WebrtcModule {}
