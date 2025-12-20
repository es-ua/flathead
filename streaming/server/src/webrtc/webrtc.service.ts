import { Injectable, Logger } from '@nestjs/common';
import { StreamService } from '../stream/stream.service';

const wrtc = require('wrtc');
const { RTCPeerConnection, RTCSessionDescription } = wrtc;

interface PeerConnection {
  pc: RTCPeerConnection;
  clientId: string;
  cameraId: string;
  createdAt: Date;
}

@Injectable()
export class WebrtcService {
  private readonly logger = new Logger(WebrtcService.name);
  private connections = new Map<string, PeerConnection>();

  private readonly rtcConfig = {
    iceServers: [
      { urls: 'stun:stun.l.google.com:19302' },
      { urls: 'stun:stun1.l.google.com:19302' },
    ],
  };

  constructor(private readonly streamService: StreamService) {}

  async createPeerConnection(
    clientId: string,
    cameraId: string,
  ): Promise<RTCPeerConnection> {
    const connectionId = `${clientId}-${cameraId}`;

    if (this.connections.has(connectionId)) {
      this.logger.warn(`Closing existing connection for ${connectionId}`);
      await this.closePeerConnection(clientId, cameraId);
    }

    const pc = new RTCPeerConnection(this.rtcConfig);

    pc.ontrack = (event: RTCTrackEvent) => {
      this.logger.log(`Received track from ${connectionId}: ${event.track.kind}`);

      if (event.track.kind === 'video') {
        this.streamService.handleVideoTrack(clientId, cameraId, event.track);
      }
    };

    pc.oniceconnectionstatechange = () => {
      this.logger.log(
        `ICE connection state for ${connectionId}: ${pc.iceConnectionState}`,
      );

      if (
        pc.iceConnectionState === 'disconnected' ||
        pc.iceConnectionState === 'failed'
      ) {
        this.closePeerConnection(clientId, cameraId);
      }
    };

    pc.onconnectionstatechange = () => {
      this.logger.log(
        `Connection state for ${connectionId}: ${pc.connectionState}`,
      );
    };

    this.connections.set(connectionId, {
      pc,
      clientId,
      cameraId,
      createdAt: new Date(),
    });

    this.logger.log(`Created peer connection for ${connectionId}`);
    return pc;
  }

  async handleOffer(
    clientId: string,
    cameraId: string,
    offer: RTCSessionDescriptionInit,
  ): Promise<RTCSessionDescriptionInit> {
    const pc = await this.createPeerConnection(clientId, cameraId);

    await pc.setRemoteDescription(new RTCSessionDescription(offer));
    this.logger.log(`Set remote description for ${clientId}-${cameraId}`);

    const answer = await pc.createAnswer();
    await pc.setLocalDescription(answer);
    this.logger.log(`Created answer for ${clientId}-${cameraId}`);

    return {
      type: answer.type,
      sdp: answer.sdp,
    };
  }

  async handleIceCandidate(
    clientId: string,
    cameraId: string,
    candidate: RTCIceCandidateInit,
  ): Promise<void> {
    const connectionId = `${clientId}-${cameraId}`;
    const connection = this.connections.get(connectionId);

    if (!connection) {
      this.logger.warn(`No connection found for ${connectionId}`);
      return;
    }

    try {
      await connection.pc.addIceCandidate(candidate);
      this.logger.debug(`Added ICE candidate for ${connectionId}`);
    } catch (error) {
      this.logger.error(`Failed to add ICE candidate: ${error}`);
    }
  }

  async closePeerConnection(clientId: string, cameraId: string): Promise<void> {
    const connectionId = `${clientId}-${cameraId}`;
    const connection = this.connections.get(connectionId);

    if (connection) {
      connection.pc.close();
      this.connections.delete(connectionId);
      this.streamService.removeTrack(clientId, cameraId);
      this.logger.log(`Closed connection ${connectionId}`);
    }
  }

  async closeAllConnectionsForClient(clientId: string): Promise<void> {
    for (const [connectionId, connection] of this.connections) {
      if (connection.clientId === clientId) {
        connection.pc.close();
        this.connections.delete(connectionId);
        this.streamService.removeTrack(clientId, connection.cameraId);
        this.logger.log(`Closed connection ${connectionId}`);
      }
    }
  }

  getConnectionStats(): {
    total: number;
    connections: Array<{
      connectionId: string;
      cameraId: string;
      state: string;
      createdAt: Date;
    }>;
  } {
    const connections = Array.from(this.connections.entries()).map(
      ([connectionId, conn]) => ({
        connectionId,
        cameraId: conn.cameraId,
        state: conn.pc.connectionState,
        createdAt: conn.createdAt,
      }),
    );

    return {
      total: this.connections.size,
      connections,
    };
  }
}
