import { Component, ViewChild, ElementRef, OnInit, OnDestroy } from '@angular/core';

@Component({
  selector: 'app-camera',
  templateUrl: './camera.component.html',
  styleUrls: ['./camera.component.css'],
})
export class CameraComponent implements OnInit, OnDestroy {
  @ViewChild('videoElement') videoElement!: ElementRef<HTMLVideoElement>;
  @ViewChild('overlayCanvas') overlayCanvas!: ElementRef<HTMLCanvasElement>;

  protected isStreaming = false;
  protected errorMessage = '';
  private animationId: number | null = null;

  ngOnInit() {
    this.startCamera();
  }

  ngOnDestroy() {
    this.stopCamera();
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
    }
  }

  private startCamera() {
    navigator.mediaDevices
      .getUserMedia({ video: { facingMode: 'user' } })
      .then((stream) => {
        if (this.videoElement?.nativeElement) {
          this.videoElement.nativeElement.srcObject = stream;
          this.isStreaming = true;
          this.drawGuideLines();
        }
      })
      .catch((err) => {
        this.errorMessage = `Camera access denied: ${err.message}`;
      });
  }

  private drawGuideLines() {
    const canvas = this.overlayCanvas?.nativeElement;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const w = canvas.width;
    const h = canvas.height;
    const lineColor = '#00ff00';
    const lineWidth = 1;

    const animate = () => {
      ctx.clearRect(0, 0, w, h);

      ctx.strokeStyle = lineColor;
      ctx.lineWidth = lineWidth;

      // Center crosshair
      const centerX = w / 2;
      const centerY = h / 2;
      const crossSize = 30;

      ctx.beginPath();
      ctx.moveTo(centerX - crossSize, centerY);
      ctx.lineTo(centerX + crossSize, centerY);
      ctx.stroke();

      ctx.beginPath();
      ctx.moveTo(centerX, centerY - crossSize);
      ctx.lineTo(centerX, centerY + crossSize);
      ctx.stroke();

      // Face guide rectangle (ratio 1:1.3 for face)
      const rectWidth = w * 0.5;
      const rectHeight = rectWidth * 1.3;
      const rectX = (w - rectWidth) / 2;
      const rectY = (h - rectHeight) / 2;

      ctx.strokeStyle = lineColor;
      ctx.lineWidth = lineWidth;
      ctx.strokeRect(rectX, rectY, rectWidth, rectHeight);

      // Corner markers
      const cornerSize = 20;
      const corners = [
        [rectX, rectY],
        [rectX + rectWidth, rectY],
        [rectX, rectY + rectHeight],
        [rectX + rectWidth, rectY + rectHeight],
      ];

      corners.forEach(([x, y]) => {
        ctx.beginPath();
        ctx.moveTo(x, y - cornerSize);
        ctx.lineTo(x, y);
        ctx.lineTo(x + cornerSize, y);
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(x + cornerSize, y - cornerSize);
        ctx.lineTo(x - cornerSize, y - cornerSize);
        ctx.lineTo(x - cornerSize, y + cornerSize);
        ctx.stroke();
      });

      this.animationId = requestAnimationFrame(animate);
    };

    animate();
  }

  private stopCamera() {
    if (this.videoElement?.nativeElement?.srcObject) {
      const stream = this.videoElement.nativeElement.srcObject as MediaStream;
      stream.getTracks().forEach((track) => track.stop());
    }
  }
}
