from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import numpy as np

def adjust_background_music(voice_path, music_path, output_path):
    # Đọc file âm thanh
    voice = AudioSegment.from_file(voice_path)
    music = AudioSegment.from_file(music_path)
    
    # Phát hiện các đoạn không im lặng trong giọng nói
    nonsilent_ranges = detect_nonsilent(voice, min_silence_len=100, silence_thresh=-50)
    
    # Tạo một bản sao của nhạc nền để điều chỉnh
    music = music - 20  # Giảm âm lượng nhạc nền
    combined = AudioSegment.silent(duration=len(voice))  # Tạo một đoạn âm thanh im lặng cùng độ dài với giọng nói
    
    # Chèn nhạc nền vào giọng nói
    for start, end in nonsilent_ranges:
        combined = combined.overlay(music, position=start)
    
    # Xuất file âm thanh kết hợp
    combined.export(output_path, format="mp3")

# Đường dẫn tới file giọng nói và nhạc nền
voice_path = 'voice.mp3'
music_path = 'background_music.mp3'
output_path = 'output_with_music.mp3'

adjust_background_music(voice_path, music_path, output_path)
