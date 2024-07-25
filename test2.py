import os
import re
from datetime import datetime, timedelta

# Hàm để trích xuất thời gian bắt đầu và kết thúc từ nội dung tệp SRT
def extract_frame_times(srt_content):
    # Sử dụng regex để tìm các thời gian bắt đầu và kết thúc trong tệp SRT
    time_pattern = re.compile(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})')
    matches = time_pattern.findall(srt_content)
    print(matches)
    return matches

# Hàm để chuyển đổi thời gian từ chuỗi HH:MM:SS,ms sang giây
def convert_to_seconds(time_str):
    time_format = '%H:%M:%S,%f'
    dt = datetime.strptime(time_str, time_format)
    delta = timedelta(hours=dt.hour, minutes=dt.minute, seconds=dt.second, microseconds=dt.microsecond)
    return delta.total_seconds()

# Đường dẫn tới tệp SRT
path = 'demo_en.srt'

# Đọc nội dung tệp SRT
with open(path, 'r', encoding='utf-8') as file:
    srt_content = file.read()

# Trích xuất thời gian các đoạn phụ đề
data = extract_frame_times(srt_content)

# Tính toán thời lượng của các đoạn phụ đề
durations = []
for start, end in data:
    duration = convert_to_seconds(end) - convert_to_seconds(start)
    durations.append(duration)

# In thời gian của đoạn đầu tiên và tất cả các đoạn khác
if durations:
    print(f"Thời gian của đoạn đầu tiên: {durations[0]} giây")
    for i, duration in enumerate(durations, 1):
        print(f"Thời gian của đoạn {i}: {duration} giây")
