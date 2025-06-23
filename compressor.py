import cv2
import os
import argparse
import math

FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"  # Path to ffmpeg

def estimate_mobile_settings(input_path, target_size_mb=100):
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise ValueError("❌ Failed to open video file.")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    duration = frames / fps
    original_size_mb = os.path.getsize(input_path) / (1024 * 1024)
    compression_ratio = target_size_mb / original_size_mb

    # Mobile screen target: 720x1280 (portrait)
    # Swap if input is landscape and force portrait resolution
    if width > height:
        width, height = height, width  # Rotate to portrait

    target_height = 1280
    target_width = int((width / height) * target_height)

    # Scale down if original is smaller than target
    target_width = min(target_width, width)
    target_height = min(target_height, height)

    # Adjust fps and CRF for size and battery-friendly performance
    new_fps = max(15, int(fps * 0.85))
    crf = min(35, 23 + (1 - compression_ratio) * 20)

    return target_width, target_height, new_fps, int(crf)

def compress_video(input_path, output_path, target_size_mb=100):
    if not os.path.exists(input_path):
        print(f"❌ Input file not found: {input_path}")
        return False

    try:
        width, height, fps, crf = estimate_mobile_settings(input_path, target_size_mb)
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    print(f"📦 Compressing '{input_path}' for mobile screen (~{target_size_mb}MB)")
    print(f"🔧 Settings: {width}x{height}, {fps} fps, CRF={crf}")

    cmd = (
        f'{FFMPEG_PATH} -i "{input_path}" -vf "scale={width}:{height}" '
        f'-r {fps} -c:v libx264 -crf {crf} -preset slow '
        f'-c:a aac -b:a 96k "{output_path}"'
    )

    print(f"🚀 Running command:\n{cmd}\n")
    result = os.system(cmd)
    return result == 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="📱 Mobile Video Compressor")
    parser.add_argument("input", help="Input video file (e.g., video.mp4)")
    parser.add_argument("output", help="Output file (e.g., output.mp4)")
    parser.add_argument("--size", type=int, default=100, help="Target size in MB (default: 100MB)")

    args = parser.parse_args()

    success = compress_video(args.input, args.output, args.size)
    if success and os.path.exists(args.output):
        final_mb = os.path.getsize(args.output) / (1024 * 1024)
        print(f"✅ Done. Output size: {final_mb:.2f} MB")
    else:
        print("❌ Compression failed.")
