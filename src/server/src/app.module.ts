import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { StreamingModule } from './streaming/streaming.module';
import { RobotsModule } from './robots/robots.module';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      envFilePath: ['.env.local', '.env'],
    }),
    StreamingModule,
    RobotsModule,
  ],
})
export class AppModule {}
