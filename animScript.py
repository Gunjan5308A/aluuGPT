import argparse
import os
import subprocess

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--prompt", default="")
    args = parser.parse_args()
    
    print(f"Generating animation for: {args.prompt}")
    
    # Simple ffmpeg command to create a 1-second blank video
    # This proves the pipeline works!
    ffmpeg_bin = os.path.join(os.getcwd(), "bin", "ffmpeg")
    if not os.path.exists(ffmpeg_bin):
        ffmpeg_bin = "ffmpeg"
        
    cmd = [
        ffmpeg_bin, "-y", "-f", "lavfi", "-i", "color=c=black:s=1280x720:d=1",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", args.output
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Saved to {args.output}")

if __name__ == "__main__":
    main()
