import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  app.enableCors({
    origin: '*',
    methods: ['GET', 'POST'],
  });

  const port = process.env.PORT || 8080;
  await app.listen(port);

  console.log(`Flathead streaming server running on port ${port}`);
}

bootstrap();
