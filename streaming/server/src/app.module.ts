import { Module } from '@nestjs/common';
import { WebrtcModule } from './webrtc/webrtc.module';
import { StreamModule } from './stream/stream.module';

@Module({
  imports: [WebrtcModule, StreamModule],
})
export class AppModule {}
