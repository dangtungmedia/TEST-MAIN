import random
import subprocess
import os
import json
import re
import requests



def extract_subtitles(srt_content):
    # Định dạng để phân tích nội dung phụ đề
    subtitle_pattern = re.compile(
        r'(\d+)\s*'              # Số thứ tự
        r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\s*' # Thời gian
        r'(.*?)\s*(?=\d+\s*\d{2}:\d{2}|\Z)', # Văn bản
        re.DOTALL
    )
    
    subtitles = []
    for match in subtitle_pattern.finditer(srt_content):
        index = match.group(1)
        start_time = match.group(2)
        end_time = match.group(3)
        text = match.group(4).strip().replace('\n', ' ')
        subtitles.append({
            'index': index,
            'start_time': start_time,
            'end_time': end_time,
            'text': text
        })
    return subtitles

def get_subtitles(video_id):
    # Đọc file phụ đề
    srt_file = f'{video_id}.vi.srt'
    with open(srt_file, 'r') as f:
        srt_content = f.read()
    
    # Xóa file phụ đề
    os.remove(srt_file)
    
    return extract_subtitles(srt_content)
