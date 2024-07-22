from pydub import AudioSegment
from pydub.silence import detect_nonsilent
<<<<<<< HEAD
import numpy as np

def adjust_background_music(voice_path, music_path, output_path):
=======
import math

def adjust_background_music(voice_path, music_path, output_path, fade_duration=2000):
>>>>>>> 910b2c93e7d7f2a4dacf696357eabd56bfaaba75
    # Đọc file âm thanh
    voice = AudioSegment.from_file(voice_path)
    music = AudioSegment.from_file(music_path)
    
<<<<<<< HEAD
    # Phát hiện các đoạn không im lặng trong giọng nói
    nonsilent_ranges = detect_nonsilent(voice, min_silence_len=100, silence_thresh=-50)
    
    # Tạo một bản sao của nhạc nền để điều chỉnh
    music = music - 20  # Giảm âm lượng nhạc nền
    combined = AudioSegment.silent(duration=len(voice))  # Tạo một đoạn âm thanh im lặng cùng độ dài với giọng nói
    
    # Chèn nhạc nền vào giọng nói
    for start, end in nonsilent_ranges:
        combined = combined.overlay(music, position=start)
=======
    # Chỉnh âm lượng nhạc nền
    db_reduction_during_speech = 20 * math.log10(0.03)  # Giảm âm lượng nhạc nền xuống 6%
    db_reduction_without_speech = 20 * math.log10(0.15)  # Giảm âm lượng nhạc nền xuống 14%
    
    # Phát hiện các đoạn không im lặng trong giọng nói
    nonsilent_ranges = detect_nonsilent(voice, min_silence_len=500, silence_thresh=voice.dBFS-16)
    
    # Tạo bản sao của nhạc nền để điều chỉnh
    adjusted_music = AudioSegment.silent(duration=len(voice))
    
    current_position = 0
    for start, end in nonsilent_ranges:
        # Chèn nhạc nền trong khoảng trước đoạn giọng nói (nếu có)
        if start > current_position:
            segment = music[current_position:start].apply_gain(db_reduction_without_speech).fade_in(fade_duration // 2).fade_out(fade_duration // 2)
            adjusted_music = adjusted_music.overlay(segment, position=current_position)
        
        # Chèn nhạc nền trong đoạn có giọng nói
        segment = music[start:end].apply_gain(db_reduction_during_speech)
        adjusted_music = adjusted_music.overlay(segment, position=start,loop=True)
        
        current_position = end
    
    # Chèn nhạc nền sau đoạn giọng nói cuối cùng (nếu có)
    if current_position < len(voice):
        segment = music[current_position:].apply_gain(db_reduction_without_speech).fade_in(fade_duration // 2)
        adjusted_music = adjusted_music.overlay(segment, position=current_position)
    
    # Thêm giọng nói vào nhạc nền đã điều chỉnh
    combined = adjusted_music.overlay(voice, loop=False)
>>>>>>> 910b2c93e7d7f2a4dacf696357eabd56bfaaba75
    
    # Xuất file âm thanh kết hợp
    combined.export(output_path, format="mp3")

# Đường dẫn tới file giọng nói và nhạc nền
voice_path = 'voice.mp3'
<<<<<<< HEAD
music_path = 'background_music.mp3'
output_path = 'output_with_music.mp3'
=======
music_path = 'news-time-141357.mp3'
output_path = 'out.mp3'
>>>>>>> 910b2c93e7d7f2a4dacf696357eabd56bfaaba75

adjust_background_music(voice_path, music_path, output_path)
