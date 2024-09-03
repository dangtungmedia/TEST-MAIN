import random
import subprocess
import os
import json

def format_time(seconds):
    """Chuyển đổi thời gian từ giây thành định dạng hh:mm:ss.sss"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02}:{minutes:02}:{secs:06.3f}"

def get_video_duration(video_path):
    # Lệnh ffprobe để lấy thông tin video dưới dạng JSON
    command = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=duration",
        "-of", "json",
        video_path
    ]
    
    # Chạy lệnh ffprobe và lấy đầu ra
    result = subprocess.run(command, capture_output=True, text=True)
    
    # Chuyển đổi đầu ra từ JSON thành dictionary
    result_json = json.loads(result.stdout)
    
    # Lấy thời lượng từ dictionary
    duration = float(result_json['streams'][0]['duration'])
    return duration


def get_random_video_from_directory(directory_path):
    video_files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
    return os.path.join(directory_path, random.choice(video_files))


def cut_and_scale_video_random(input_video, output_video, duration, scale_width, scale_height, overlay_video_dir):
    video_length = get_video_duration(input_video)
    start_time = random.uniform(0, video_length - duration)
    
    start_time_str = format_time(start_time)
    end_time = format_time(duration)
    
    base_video = get_random_video_from_directory(overlay_video_dir)
    is_overlay_video = random.choice([True, False])
    
    if is_overlay_video:
        cmd = [
            "ffmpeg",
            "-i", input_video,
            "-ss", start_time_str,
            "-t", str(duration),
            "-i", base_video,
            "-ss", start_time_str,
            "-t", str(duration),
            "-filter_complex", f"[0:v]scale={scale_width}:{scale_height}[bg];[1:v]scale={scale_width}:{scale_height}[overlay_scaled];[bg][overlay_scaled]overlay[outv]",
            "-map", "[outv]",
            "-r", "24",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-an",  # Loại bỏ âm thanh
            "-y",  # Ghi đè file output nếu đã tồn tại
            output_video
        ]
    else:
        cmd = [
            "ffmpeg",
             "-i", input_video,
            "-ss", start_time_str,
            "-t", end_time,
            "-vf", f"scale={scale_width}:{scale_height}",
            "-r", "24",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-an",  # Loại bỏ âm thanh
            "-y",  # Ghi đè file output nếu đã tồn tại
            output_video
        ]
    
    try:
        # Chạy lệnh FFmpeg
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")


input_video = r"video\4-k-animation-brian-and-print-circuit-board-with-dot-moving-on-line-with-alpha-matt-SBV-319035980-HD.mp4"
out_file = "output.mp4"
duration = 10
# Example usage
cut_and_scale_video_random(input_video,out_file, duration, 1280, 720, 'video_screen')

