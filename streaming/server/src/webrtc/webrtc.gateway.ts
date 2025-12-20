import {
  WebSocketGateway,
  WebSocketServer,
  SubscribeMessage,
  OnGatewayConnection,
  OnGatewayDisconnect,
  MessageBody,
  ConnectedSocket,
} from '@nestjs/websockets';
import { Logger } from '@nestjs/common';
import { Server, Socket } from 'socket.io';
import { WebrtcService } from './webrtc.service';

interface OfferPayload {
  cameraId: string;
  offer: RTCSessionDescriptionInit;
}

interface IceCandidatePayload {
  cameraId: string;
  candidate: RTCIceCandidateInit;
}

@WebSocketGateway({
  cors: {
    origin: '*',
  },
  namespace: '/stream',
})
export class WebrtcGateway implements OnGatewayConnection, OnGatewayDisconnect {
  @WebSocketServer()
  server!: Server;

  private readonly logger = new Logger(WebrtcGateway.name);

  constructor(private readonly webrtcService: WebrtcService) {}

  handleConnection(client: Socket) {
    this.logger.log(`Client connected: ${client.id}`);
    client.emit('connected', { clientId: client.id });
  }

  async handleDisconnect(client: Socket) {
    this.logger.log(`Client disconnected: ${client.id}`);
    await this.webrtcService.closeAllConnectionsForClient(client.id);
  }

  @SubscribeMessage('offer')
  async handleOffer(
    @ConnectedSocket() client: Socket,
    @MessageBody() payload: OfferPayload,
  ) {
    this.logger.log(
      `Received offer from ${client.id} for camera ${payload.cameraId}`,
    );

    try {
      const answer = await this.webrtcService.handleOffer(
        client.id,
        payload.cameraId,
        payload.offer,
      );

      client.emit('answer', {
        cameraId: payload.cameraId,
        answer,
      });

      this.logger.log(`Sent answer to ${client.id} for camera ${payload.cameraId}`);
    } catch (error) {
      this.logger.error(`Error handling offer: ${error}`);
      client.emit('error', {
        cameraId: payload.cameraId,
        message: 'Failed to process offer',
      });
    }
  }

  @SubscribeMessage('ice-candidate')
  async handleIceCandidate(
    @ConnectedSocket() client: Socket,
    @MessageBody() payload: IceCandidatePayload,
  ) {
    this.logger.debug(
      `Received ICE candidate from ${client.id} for camera ${payload.cameraId}`,
    );

    try {
      await this.webrtcService.handleIceCandidate(
        client.id,
        payload.cameraId,
        payload.candidate,
      );
    } catch (error) {
      this.logger.error(`Error handling ICE candidate: ${error}`);
    }
  }

  @SubscribeMessage('disconnect-camera')
  async handleDisconnectCamera(
    @ConnectedSocket() client: Socket,
    @MessageBody() payload: { cameraId: string },
  ) {
    this.logger.log(
      `Client ${client.id} disconnecting camera ${payload.cameraId}`,
    );
    await this.webrtcService.closePeerConnection(client.id, payload.cameraId);
  }

  @SubscribeMessage('stats')
  handleStats(@ConnectedSocket() client: Socket) {
    const stats = this.webrtcService.getConnectionStats();
    client.emit('stats', stats);
  }
}
