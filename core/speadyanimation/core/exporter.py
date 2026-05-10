import subprocess
import sys


class Exporter:
    def __init__(self, width, height, fps, filename="output.mp4",
                 codec="libx264", preset="medium"):
        self.width = width
        self.height = height
        self.fps = fps
        self.filename = filename
        self.codec = codec
        self.preset = preset
        self.process = None
        self.frame_count = 0

        # Use local ffmpeg if available (essential for Vercel)
        ffmpeg_bin = os.path.join(os.getcwd(), "bin", "ffmpeg")
        if not os.path.exists(ffmpeg_bin):
            ffmpeg_bin = "ffmpeg" # Fallback to system path

        command = [
            ffmpeg_bin,
            '-y',

            '-f', 'rawvideo',
            '-vcodec', 'rawvideo',
            '-s', f'{self.width}x{self.height}',
            '-pix_fmt', 'rgb24',
            '-r', str(self.fps),
            '-i', '-',
            '-c:v', self.codec,
            '-preset', self.preset,
            '-pix_fmt', 'yuv420p',
            '-crf', '18',
            self.filename,
        ]
        try:
            self.process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
            print(f"[Exporter] Recording to {self.filename} ({self.width}x{self.height} @ {self.fps}fps)")
        except FileNotFoundError:
            print("[Exporter] ERROR: ffmpeg not found. Install ffmpeg to export video.")
            print("[Exporter] Falling back to frame export mode.")
            self.process = None

    def write_frame(self, frame_bytes):
        if self.process and self.process.stdin:
            try:
                self.process.stdin.write(frame_bytes)
                self.frame_count += 1
            except BrokenPipeError:
                print("[Exporter] ERROR: FFmpeg pipe broken.")
                self.process = None

    def finish(self):
        if self.process:
            try:
                self.process.stdin.close()
                self.process.wait(timeout=30)
                print(f"[Exporter] Done. {self.frame_count} frames written to {self.filename}")
            except Exception as e:
                print(f"[Exporter] Error finalizing: {e}")
                try:
                    self.process.kill()
                except Exception:
                    pass
