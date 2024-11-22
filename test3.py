import os
import random
from datetime import datetime
import subprocess
from tqdm import tqdm  # Thư viện hiển thị tiến trình

# Chuyển đổi end_time thành timedelta
end_time = "0:00:27.669751"
end_time = datetime.strptime(end_time, "%H:%M:%S.%f") - datetime(1900, 1, 1)
end_time_in_seconds = end_time.total_seconds()
print(end_time_in_seconds)
# Thư mục nhạc nền
background_music_folder = "music_background"
if not os.path.exists(background_music_folder):
    raise FileNotFoundError(f"The folder {background_music_folder} does not exist.")

music_files = [f for f in os.listdir(background_music_folder) if f.endswith(('.mp3', '.wav'))]
if not music_files:
    raise FileNotFoundError("No .mp3 or .wav files found in the music_background folder.")

background_music = os.path.join(background_music_folder, random.choice(music_files))
start_time = random.uniform(0, max(0, end_time_in_seconds - 10))

# Đường dẫn tệp video và phụ đề
file_video = "media/6860/input_files_video.txt"
file_sub = "media/6860/subtitles.ass"
video_id = "6860"
name_video = "g7ZQBOF"

if not os.path.isfile(file_video):
    raise FileNotFoundError(f"The file {file_video} does not exist.")
if not os.path.isfile(file_sub):
    raise FileNotFoundError(f"The subtitle file {file_sub} does not exist.")

# Đảm bảo thư mục đầu ra tồn tại
os.makedirs(f"media/{video_id}", exist_ok=True)

# Tính tổng thời lượng của video concat
total_duration = end_time_in_seconds
if total_duration is None:
    raise ValueError("Could not determine the total duration of the video.")

# Lệnh FFmpeg
ffmpeg_command = [
    'ffmpeg',
    '-f', 'concat',
    '-safe', '0',
    '-i', file_video,
    '-vf', f"subtitles={file_sub}",
    '-c:v', 'libx264',
    '-c:a', 'copy',
    '-map', '0:v',
    '-map', '0:a',
    '-y',
    f"media/{video_id}/cache_video.mp4"
]

# Chạy FFmpeg và hiển thị tiến trình
print(f"Running FFmpeg command:\n{' '.join(ffmpeg_command)}")
with subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True) as process:
    for line in process.stderr:
        if "time=" in line:
            # Lấy giá trị thời gian từ log
            time_str = line.split("time=")[1].split(" ")[0].strip()
            h, m, s = map(float, time_str.split(":"))
            current_time = int(h * 3600 + m * 60 + s)
            # Hiển thị tỉ lệ hoàn thành
            percentage = (current_time / total_duration) * 100
            print(f"Tỉ lệ hoàn thành: {percentage:.2f}%")
    process.wait()

# Kiểm tra lỗi từ FFmpeg
if process.returncode != 0:
    print(f"FFmpeg error:\n{process.stderr.read()}")
else:
    print(f"Output file created successfully: media/{video_id}/{name_video}.mp4")


background_music_folder = "music_background"  # Thay đổi thành đường dẫn thư mục chứa nhạc của bạn

music_files = [f for f in os.listdir(background_music_folder) if f.endswith(('.mp3', '.wav'))]

background_music = os.path.join(background_music_folder, random.choice(music_files))

start_time = random.uniform(0, max(0, total_duration - 10))  # Chọn ngẫu nhiên thời gian bắt đầu, ít nhất là 10s trước khi hết file.

ffmpeg_bgm_command = [
    'ffmpeg',
    '-i', f"media/{video_id}/cache_video.mp4",  # Tệp video
    '-i', background_music,  # Tệp nhạc nền
    '-filter_complex', f"[1]atrim=start={start_time}:duration={total_duration},volume=0.15[bgm];[0][bgm]amix=inputs=2:duration=longest",
    '-y', f"media/{video_id}/{name_video}.mp4"  # Đầu ra video
]

print(f"Running FFmpeg command:\n{' '.join(ffmpeg_bgm_command)}")

with subprocess.Popen(ffmpeg_bgm_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True) as process:
    for line in process.stderr:
        if "time=" in line:
            try:
                time_str = line.split("time=")[1].split(" ")[0].strip()
                if time_str == "N/A":
                    continue  # Bỏ qua nếu không có thông tin thời gian
                h, m, s = map(float, time_str.split(":"))
                current_time = int(h * 3600 + m * 60 + s)
                percentage = (current_time / total_duration) * 100
                print(f"Tỉ lệ hoàn thành video backrought: {percentage:.2f}%")
            except Exception as e:
                print(f"Error parsing time: {e}")
    process.wait()

# Kiểm tra lỗi sau khi kết thúc
if process.returncode != 0:
    print("FFmpeg encountered an error.")
    stderr_output = ''.join(process.stderr)
    print(f"Error log:\n{stderr_output}")
else:
    print("Lồng nhạc nền thành công.")
