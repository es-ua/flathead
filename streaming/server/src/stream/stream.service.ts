import { Injectable, Logger } from '@nestjs/common';
import { EventEmitter } from 'events';

interface VideoTrackInfo {
  clientId: string;
  cameraId: string;
  track: MediaStreamTrack;
  addedAt: Date;
}

export interface FrameEvent {
  clientId: string;
  cameraId: string;
  timestamp: number;
  frame: Buffer;
}

@Injectable()
export class StreamService extends EventEmitter {
  private readonly logger = new Logger(StreamService.name);
  private tracks = new Map<string, VideoTrackInfo>();

  constructor() {
    super();
  }

  handleVideoTrack(
    clientId: string,
    cameraId: string,
    track: MediaStreamTrack,
  ): void {
    const trackId = `${clientId}-${cameraId}`;

    this.tracks.set(trackId, {
      clientId,
      cameraId,
      track,
      addedAt: new Date(),
    });

    this.logger.log(`Video track registered: ${trackId}`);

    track.onended = () => {
      this.logger.log(`Video track ended: ${trackId}`);
      this.removeTrack(clientId, cameraId);
    };

    track.onmute = () => {
      this.logger.warn(`Video track muted: ${trackId}`);
    };

    track.onunmute = () => {
      this.logger.log(`Video track unmuted: ${trackId}`);
    };

    this.emit('track-added', { clientId, cameraId, track });
  }

  removeTrack(clientId: string, cameraId: string): void {
    const trackId = `${clientId}-${cameraId}`;
    const trackInfo = this.tracks.get(trackId);

    if (trackInfo) {
      trackInfo.track.stop();
      this.tracks.delete(trackId);
      this.emit('track-removed', { clientId, cameraId });
      this.logger.log(`Video track removed: ${trackId}`);
    }
  }

  getTrack(clientId: string, cameraId: string): MediaStreamTrack | undefined {
    const trackId = `${clientId}-${cameraId}`;
    return this.tracks.get(trackId)?.track;
  }

  getAllTracks(): VideoTrackInfo[] {
    return Array.from(this.tracks.values());
  }

  getTracksForClient(clientId: string): VideoTrackInfo[] {
    return Array.from(this.tracks.values()).filter(
      (t) => t.clientId === clientId,
    );
  }

  getStats(): {
    totalTracks: number;
    tracksByCamera: Record<string, number>;
  } {
    const tracksByCamera: Record<string, number> = {};

    for (const track of this.tracks.values()) {
      tracksByCamera[track.cameraId] = (tracksByCamera[track.cameraId] || 0) + 1;
    }

    return {
      totalTracks: this.tracks.size,
      tracksByCamera,
    };
  }
}
