import os
import subprocess
from PIL import Image
from os.path import join
from PIL.Image import Resampling

# Input and output directories
input_dir = "videos"
output_dir = "output"

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Retrieve all .mp4 files from the input video folder
files = [f for f in os.listdir(input_dir) if f.endswith(".mp4")]

for idx, file in enumerate(files):
    input_file = join(input_dir, file)
    output_file = join(output_dir, file)

    # Check video dimensions using subprocess with ffprobe
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "csv=p=0:s=x",
        input_file
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    width, height = map(int, result.stdout.strip().split('x'))
    
    # Adjust the width for overlay
    base_width = width - 20  # Adjusted width for overlay

    # Resize overlay image to fit video
    overlay_image = Image.open('overlay.png')
    overlay_ratio = base_width / overlay_image.width
    overlay_resized = overlay_image.resize((base_width, int(overlay_image.height * overlay_ratio)), Resampling.LANCZOS)
    overlay_resized.save("temp.png")

    # Overlay video with FFmpeg
    cmd = [
        "ffmpeg", "-i", input_file,
        "-i", "temp.png",
        "-filter_complex", f"[0:v][1:v] overlay=10:10,scale={width*2}:-1",
        "-c:a", "copy",
        "-y", output_file
    ]
    subprocess.run(cmd)

    # Clean up temporary overlay file
    os.remove("temp.png")

    # Display progress
    print(f"Processed {idx + 1}/{len(files)} videos: {file}")
