import cv2
import os
import argparse
import math
import subprocess

# ✅ No quotes here — subprocess handles it
FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"

def estimate_compression_settings(input_path, target_size_mb=1024):
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise ValueError("Failed to open video file.")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    duration = frames / fps if fps else 0
    original_size_mb = os.path.getsize(input_path) / (1024 * 1024)

    if original_size_mb <= 0 or duration <= 0:
        raise ValueError("Invalid video size or duration.")

    compression_ratio = target_size_mb / original_size_mb
    resolution_scale = math.sqrt(compression_ratio) * 0.8

    new_width = max(320, min(width, int(width * resolution_scale)))
    new_height = max(240, min(height, int(height * resolution_scale)))
    new_fps = max(15, int(fps * 0.9))
    crf = min(35, 23 + (1 - compression_ratio) * 20)

    return new_width, new_height, new_fps, int(crf)

def compress_video(input_path, output_path, target_size_mb=1024):
    if not os.path.exists(input_path):
        print(f"Input file not found: {input_path}")
        return False

    try:
        width, height, fps, crf = estimate_compression_settings(input_path, target_size_mb)
    except Exception as e:
        print(f"Error: {e}")
        return False

    print(f"Compressing '{input_path}' to ~{target_size_mb}MB")
    print(f"Settings: {width}x{height}, {fps} fps, CRF={crf}")

    # ✅ Use subprocess list for safety (no string formatting issues)
    cmd = [
        FFMPEG_PATH,
        "-i", input_path,
        "-vf", f"scale={width}:{height}",
        "-r", str(fps),
        "-c:v", "libx264",
        "-crf", str(crf),
        "-preset", "slow",
        "-c:a", "aac",
        "-b:a", "128k",
        output_path
    ]

    print("Running:", " ".join(cmd))
    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple Video Compressor")
    parser.add_argument("input", help="Input video file path")
    parser.add_argument("output", help="Output video file path")
    parser.add_argument("--size", type=int, default=100, help="Target size in MB (default: 100MB)")

    args = parser.parse_args()

    success = compress_video(args.input, args.output, args.size)
    if success and os.path.exists(args.output):
        final_size = os.path.getsize(args.output) / (1024 * 1024)
        print(f"Done. Output size: {final_size:.2f} MB")
    else:
        print("Compression failed.")
