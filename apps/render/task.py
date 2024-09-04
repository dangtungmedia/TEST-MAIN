import os
from celery import shared_task, Celery
import os, shutil, urllib
import time
from django.core.files.storage import default_storage
from django.core.cache import cache
from apps.render.models import VideoRender
import requests
import json
import subprocess, random
from datetime import timedelta
from pydub import AudioSegment
from PIL import Image, ImageDraw, ImageFont
import base64
from celery.signals import task_failure, worker_shutdown
from celery.utils.log import get_task_logger
import os, environ

from gtts import gTTS

import edge_tts
import asyncio

from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import math

import os
import requests
import urllib

import edge_tts, random, subprocess
import asyncio, json, shutil
from pydub import AudioSegment
import nltk
from googletrans import Translator
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import math
from datetime import timedelta, datetime
from pydub import AudioSegment
from PIL import Image, ImageDraw, ImageFont
from requests_toolbelt.multipart.encoder import MultipartEncoder, MultipartEncoderMonitor
import re
from datetime import datetime, timedelta
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from celery.result import AsyncResult
from celery import shared_task, signals

import whisper
import re
from yt_dlp import YoutubeDL
from pytube import YouTube

import librosa

SECRET_KEY="ugz6iXZ.fM8+9sS}uleGtIb,wuQN^1J%EvnMBeW5#+CYX_ej&%"
SERVER='http://daphne:5504'

@task_failure.connect
def task_failure_handler(sender, task_id, exception, args, kwargs, traceback, einfo, **kw):
    video_id = args[0].get('video_id')
    worker_id = "None"
    update_status_video("Render Lỗi : Lỗi Render Không Xác Định", video_id, task_id, worker_id)

@worker_shutdown.connect
def worker_shutdown_handler(sender, **kwargs):
    worker_id = sender.hostname
    for video in VideoRender.objects.filter(worker_id=worker_id):
        if "Đang Render" in video.status_video or "Đang Chờ Render" in video.status_video:
            video.status_video = f'Render Lỗi : Worker bị tắt đột ngột {worker_id}'
            video.save()

@shared_task(bind=True, priority=0)
def render_video(self, data):
    task_id = render_video.request.id
    worker_id = render_video.request.hostname  # Lưu worker ID
    video_id = data.get('video_id')

    update_status_video("Đang Render : Đang lấy thông tin video render", data['video_id'], task_id, worker_id)
    success = create_or_reset_directory(f'media/{video_id}')

    if not success:
        shutil.rmtree(f'media/{video_id}')
        update_status_video("Render Lỗi : Không thể tạo thư mục", data['video_id'], task_id, worker_id)
        return
    update_status_video("Đang Render : Tạo thư mục thành công", data['video_id'], task_id, worker_id)

    # Tải xuống hình ảnh
    success = download_image(data, task_id, worker_id)
    if not success:
        shutil.rmtree(f'media/{video_id}')
        update_status_video("Render Lỗi : Không thể tải xuống hình ảnh", data['video_id'], task_id, worker_id)
        return
    update_status_video("Đang Render : Tải xuống hình ảnh thành công", data['video_id'], task_id, worker_id)

    if not data.get('url_audio'):
        # Tải xuống âm thanh
        success = download_audio(data, task_id, worker_id)
        if not success:
            update_status_video("Render Lỗi : Không thể tải xuống âm thanh", data['video_id'], task_id, worker_id)
            shutil.rmtree(f'media/{video_id}')
            return
        update_status_video("Đang Render : Tải xuống âm thanh thành công", data['video_id'], task_id, worker_id)

    #nối giọng đọc và chèn nhạc nền
    success = merge_audio_video(data, task_id, worker_id)
    if not success:
        shutil.rmtree(f'media/{video_id}')
        update_status_video("Render Lỗi : Không thể nối giọng đọc và chèn nhạc nền", data['video_id'], task_id, worker_id)
        return
    update_status_video("Đang Render : Nối giọng đọc và chèn nhạc nền thành công", data['video_id'], task_id, worker_id)


    # Tạo video
    success = create_video_lines(data, task_id, worker_id)
    if not success:
        shutil.rmtree(f'media/{video_id}')
        update_status_video("Render Lỗi : Không thể tạo video", data['video_id'], task_id, worker_id)
        return
    update_status_video("Đang Render : Tạo video thành công", data['video_id'], task_id, worker_id)


    # Tạo phụ đề cho video
    success = create_subtitles(data, task_id, worker_id)
    if not success:
        shutil.rmtree(f'media/{video_id}')
        update_status_video("Render Lỗi : Không thể tạo phụ đề", data['video_id'], task_id, worker_id)
        return
    update_status_video("Đang Render : Tạo phụ đề thành công", data['video_id'], task_id, worker_id)

    # Tạo file
    success = create_video_with_retries(data, task_id, worker_id)
    if not success:
        shutil.rmtree(f'media/{video_id}')
        update_status_video("Render Lỗi : Không thể tạo file", data['video_id'], task_id, worker_id)
        return
    
    update_status_video("Đang Render : Tạo file thành công", data['video_id'], task_id, worker_id)
    time.sleep(5)

    success = upload_video(data, task_id, worker_id)
    if not success:
        update_status_video("Render Lỗi : Không thể upload video", data['video_id'], task_id, worker_id)
        return
    
    update_status_video(f"Render Thành Công : Đang Chờ Upload lên Kênh", data['video_id'], task_id, worker_id)


@shared_task(bind=True, priority=10)
def render_video_reupload(self, data):
    print(data)
    task_id = render_video.request.id
    worker_id = render_video.request.hostname 
    video_id = data.get('video_id')
    update_status_video("Đang Render : Đang lấy thông tin video render", data['video_id'], task_id, worker_id)
    
    success = update_info_video(data, task_id, worker_id)
    if not success:
        update_status_video("Render Lỗi : Không thể cập nhật thông tin video", data['video_id'], task_id, worker_id)
        return
    update_status_video("Đang Render : Cập nhật thông tin video thành công", data['video_id'], task_id, worker_id)
    
    
    success = create_or_reset_directory(f'media/{video_id}')
    if not success:
        shutil.rmtree(f'media/{video_id}')
        update_status_video("Render Lỗi : Không thể tạo thư mục", data['video_id'], task_id, worker_id)
        return
    success = download_image(data, task_id, worker_id)

    if not success:
        shutil.rmtree(f'media/{video_id}')
        update_status_video("Render Lỗi : Không thể tải xuống hình ảnh", data['video_id'], task_id, worker_id)
        return
    update_status_video("Đang Render : Tải xuống hình ảnh thành công", data['video_id'], task_id, worker_id)

    if data.get('url_reupload'):
        success = download_audio_reup(data, task_id, worker_id)
        if not success:
            update_status_video("Render Lỗi : Không thể tải xuống âm thanh", data['video_id'], task_id, worker_id)
            shutil.rmtree(f'media/{video_id}')
            return
        update_status_video("Đang Render : Tải xuống âm thanh thành công", data['video_id'], task_id, worker_id)
    
    success = get_sub_audio(data, task_id, worker_id)
    if not success:
        update_status_video("Render Lỗi : Không thể lấy phụ đề video", data['video_id'], task_id, worker_id)
        return
    update_status_video("Đang Render : Lấy xong phụ đề video", data['video_id'], task_id, worker_id)

    success = create_video_url_lines(data, task_id, worker_id)
    if not success:
        shutil.rmtree(f'media/{video_id}')
        update_status_video("Render Lỗi : Không thể tạo video", data['video_id'], task_id, worker_id)
        return
    update_status_video("Đang Render : Đã tạo xong video", data['video_id'], task_id, worker_id)

    success = create_subtitles_reup_url(data, task_id, worker_id)
    if not success:
        shutil.rmtree(f'media/{video_id}')
        update_status_video("Render Lỗi : Không thể tạo phụ đề", data['video_id'], task_id, worker_id)
        return

    update_status_video("Đang Render : Tạo phụ đề thành công", data['video_id'], task_id, worker_id)

    success = create_video_reup_urls(data, task_id, worker_id)
    if not success:
        shutil.rmtree(f'media/{video_id}')
        update_status_video("Render Lỗi : Lỗi tạo file video", data['video_id'], task_id, worker_id)
        return
    update_status_video("Render Lỗi : Tạo thành công video", data['video_id'], task_id, worker_id)

    success = upload_video(data, task_id, worker_id)
    if not success:
        update_status_video("Render Lỗi : Không thể upload video", data['video_id'], task_id, worker_id)
        return
    update_status_video(f"Render Thành Công : Đang Chờ Upload lên Kênh", data['video_id'], task_id, worker_id)

def upload_video(data, task_id, worker_id):
    try:
        video_id = data.get('video_id')
        name_video = data.get('name_video')
        video_path = f'media/{video_id}/{name_video}.mp4'
        url = f'{SERVER}/api/'
        update_status_video(f"Đang Render : Đang Upload File Lên Sever", video_id, task_id, worker_id)
        
        payload = {
            'video_id': str(video_id),
            'action': 'upload',
            'secret_key': SECRET_KEY
        }

        def create_multipart_encoder(file_path, fields):
            # Ensure all field values are strings
            fields = {key: str(value) for key, value in fields.items()}
            return MultipartEncoder(
                fields={**fields, 'file': (file_path, open(file_path, 'rb'), 'video/mp4')}
            )

        def create_multipart_monitor(encoder, progress_callback):
            monitor = MultipartEncoderMonitor(encoder, progress_callback)
            return monitor

        def progress_callback(monitor):
            progress = (monitor.bytes_read / monitor.len) * 100
            print(f"Upload progress: {progress:.2f}%")
            

        with open(video_path, 'rb') as f:
            encoder = create_multipart_encoder(video_path, payload)
            monitor = create_multipart_monitor(encoder, progress_callback)
            headers = {'Content-Type': monitor.content_type}

            response = requests.post(url, data=monitor, headers=headers)

            if response.status_code == 201:
                return False
            else:
                shutil.rmtree(f'media/{video_id}')
                return True
        
    except Exception as e:
        return False

def create_video_file(data, task_id, worker_id):
    video_id = data.get('video_id')
    name_video = data.get('name_video')
    text = data.get('text_content')

    # Tạo file subtitles.ass
    ass_file_path = f'media/{video_id}/subtitles.ass'

    # Tạo file input_files_video.txt
    input_files_video_path = f'media/{video_id}/input_files_video.txt'
    os.makedirs(os.path.dirname(input_files_video_path), exist_ok=True)
    with open(input_files_video_path, 'w') as file:
        for item in json.loads(text):
            file.write(f"file 'video/{item['id']}.mp4'\n")

    audio_file = f'media/{video_id}/audio.wav'
    fonts_dir = r'apps/render/font'

    # Kiểm tra sự tồn tại của file audio
    if not os.path.exists(audio_file):
        print(f"Audio file not found: {audio_file}")
        return False
    
    ffmpeg_command = [
        'ffmpeg',
        '-f', 'concat',
        '-safe', '0',
        '-i', input_files_video_path,
        '-i', audio_file,
        '-vf', f"subtitles={ass_file_path}:fontsdir={fonts_dir}",
        '-c:v', 'libx264',
        '-map', '0:v',
        '-map', '1:a',
        '-y',
        f"media/{video_id}/{name_video}.mp4"
    ]

    try:
        result = subprocess.run(ffmpeg_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except subprocess.CalledProcessError as e:
        print(f"ffmpeg failed with error: {e.stderr}")
        return False
    return True

def create_video_with_retries(data, task_id, worker_id, max_retries=10):
    for attempt in range(max_retries):
        if create_video_file(data, task_id, worker_id):
            print(f"Video creation succeeded on attempt {attempt + 1}")
            return True
        else:
            print(f"Attempt {attempt + 1} failed, retrying...")
            time.sleep(1)  # Chờ một chút trước khi thử lại
    print("Max retries reached, video creation failed.")
    return False

def find_font_file(font_name, font_dir, extensions=[".ttf", ".otf", ".woff", ".woff2"]):

    print(f"Searching for font '{font_name}' in directory '{font_dir}' with extensions {extensions}")
    for root, dirs, files in os.walk(font_dir):
        print(f"Checking directory: {root}")
        for file in files:
            print(f"Found file: {file}")
            if any(file.lower() == f"{font_name.lower()}{ext}" for ext in extensions):
                print(f"Matched font file: {file}")
                return os.path.join(root, file)
    print(f"Font '{font_name}' not found in directory '{font_dir}'")
    return None

def get_text_lines(data, text,width=1920):
    current_line = ""
    wrapped_text = ""
    font = data['font_name']
    font_text = find_font_file(font, r'apps/render/font')

    font_size = data.get('font_size')



    font = ImageFont.truetype(font_text,font_size)

    img = Image.new('RGB', (1, 1), color='black')

    draw = ImageDraw.Draw(img)

    for char in text:
        test_line = current_line + char
        bbox = draw.textbbox((0, 0), test_line, font=font)
        text_width = bbox[2] - bbox[0]

        # Kiểm tra nếu thêm dấu câu vào dòng mới vẫn giữ cho chiều rộng trên 50%
        if text_width <= width:
            current_line = test_line
        else:
            # Nếu chiều rộng vượt quá giới hạn, tìm vị trí của dấu câu cuối cùng
            last_punctuation_index = find_last_punctuation_index(current_line)
            if last_punctuation_index != -1:
                text_1 = current_line[:last_punctuation_index + 1]
                text_2 = current_line[last_punctuation_index + 1:]

                bbox_1 = draw.textbbox((0, 0), text_1, font=font)
                text_width_1 = bbox_1[2] - bbox_1[0]

                if text_width_1 <= int(width / 2):
                    text_count = find_last_punctuation_index(text_2)

                    if text_count != -1:
                        wrapped_text += text_1 + text_2[:text_count + 1] + "\\n"
                        current_line = text_2[text_count + 1:]
                    else:
                        wrapped_text += current_line + "\\n"
                        current_line = char
                else:
                    wrapped_text += text_1 + "\\n"
                    current_line = text_2
            else:
                # Nếu không tìm thấy dấu câu, thêm toàn bộ dòng vào danh sách
                wrapped_text += current_line + "\\n"
                current_line = char

    wrapped_text += current_line
    return wrapped_text

def find_last_punctuation_index(line):
    punctuation = "。、！？.,"  # Các dấu câu có thể xem xét
    last_punctuation_index = -1

    for i, char in enumerate(reversed(line)):
        if char in punctuation:
            last_punctuation_index = len(line) - i - 1
            break
    return last_punctuation_index

def format_timedelta_ass(ms):
    # Định dạng thời gian cho ASS
    total_seconds = ms.total_seconds()
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int((seconds - int(seconds)) * 100)
    seconds = int(seconds)
    return "{:01}:{:02}:{:02}.{:02}".format(int(hours), int(minutes), seconds, milliseconds)

def create_subtitles(data, task_id, worker_id):
    # try:
    video_id = data.get('video_id')
    subtitle_file = f'media/{video_id}/subtitles.ass'
    color = data.get('font_color')
    color_backrought = data.get('color_backrought')
    color_border = data.get('stroke')
    font_text = data.get("font_name")
    font_size = data.get('font_size')
    stroke_text = data.get('stroke_size')
    text  = data.get('text_content')

    with open(subtitle_file, 'w', encoding='utf-8') as ass_file:
        # Viết header cho file ASS
        ass_file.write("[Script Info]\n")
        ass_file.write("Title: Subtitles\n")
        ass_file.write("ScriptType: v4.00+\n")
        ass_file.write("WrapStyle: 0\n")
        ass_file.write("ScaledBorderAndShadow: yes\n")
        ass_file.write("YCbCr Matrix: TV.601\n")
        ass_file.write(f"PlayResX: 1920\n")
        ass_file.write(f"PlayResY: 1080\n\n")

        ass_file.write("[V4+ Styles]\n")
        ass_file.write("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n")
        ass_file.write(f"Style: Default,{font_text},{font_size},{color},{color_backrought},&H00000000,{color_border},0,0,0,0,100,100,0,0,1,{stroke_text},0,2,10,10,10,0\n\n")

        ass_file.write("[Events]\n")
        ass_file.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect,WrapStyle,Text\n")

        start_time = timedelta(0)
        
        total_entries = len(json.loads(text))
        if  data.get('file-srt'):
            srt_path = f'media/{video_id}/cache.srt'
            # Đọc nội dung tệp SRT
            with open(srt_path, 'r', encoding='utf-8') as file:
                srt_content = file.read()
            print("Nội dung của tệp SRT đã được tải và đọc thành công.")
            
            # Trích xuất thời gian các khung trong tệp SRT
            frame_times = extract_frame_times(srt_content)

            if len(frame_times) == 0:
                return False
            elif len(frame_times) != total_entries:
                return False

            elif len(frame_times) == total_entries:
                for i,iteam in enumerate(json.loads(text)):
                    start_time, end_time = frame_times[i]
                    ass_file.write(f"Dialogue: 0,{start_time[:-1].replace(',', '.')},{end_time[:-1].replace(',', '.')},Default,,0,0,0,,2,{get_text_lines(data,iteam['text'])}\n")
                return True

        for i,iteam in enumerate(json.loads(text)):
            duration = get_audio_duration(f'media/{video_id}/voice/{iteam["id"]}.wav')
            duration_milliseconds = duration * 1000
            end_time = start_time + timedelta(milliseconds=duration_milliseconds)
            # end_time = start_time + duration
            # Viết phụ đề
            ass_file.write(f"Dialogue: 0,{format_timedelta_ass(start_time)},{format_timedelta_ass(end_time)},Default,,0,0,0,,2,{get_text_lines(data,iteam['text'])}\n")
            start_time = end_time
        return True
    # except:
    #     return False

def merge_audio_video(data, task_id, worker_id):
    try:
        update_status_video("Đang Render: đang ghép giọng đọc", data['video_id'], task_id, worker_id)
        video_id = data.get('video_id')
        fade_duration = 2000

        # Tải xuống tệp âm thanh nếu có URL âm thanh
        if data.get('url_audio'):
            max_retries = 30
            retries = 0
            url_audio = f"{SERVER}{data.get('url_audio')}"
            while retries < max_retries:
                try:
                    response = requests.get(url_audio, stream=True)
                    if response.status_code == 200:
                        os.makedirs(f'media/{video_id}', exist_ok=True)
                        with open(f'media/{video_id}/cache.wav', 'wb') as file:
                            for chunk in response.iter_content(chunk_size=1024):
                                if chunk:  # Lọc bỏ các keep-alive chunks mới
                                    file.write(chunk)
                        print("Tải xuống thành công.")
                        break
                    else:
                        print(f"Lỗi {response.status_code}: Không thể tải xuống tệp.")
                except requests.RequestException as e:
                    print(f"Lỗi tải xuống: {e}")
                retries += 1
                time.sleep(5)
                print(f"Thử lại {retries}/{max_retries}")
            else:
                return False  # Nếu không thể tải xuống tệp sau nhiều lần thử
        else:
            ffmpeg_command = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', f'media/{video_id}/input_files.txt',
                '-c', 'copy',
                f'media/{video_id}/cache.wav'
            ]
            subprocess.run(ffmpeg_command, check=True)

        # Chọn nhạc nền ngẫu nhiên từ thư mục 'music_background'
        music_path = random.choice([f for f in os.listdir('music_background') if os.path.isfile(os.path.join('music_background', f))])
        music_path = os.path.join('music_background', music_path)

        voice = AudioSegment.from_file(f'media/{video_id}/cache.wav')
        music = AudioSegment.from_file(music_path)

        # Lặp lại nhạc nền để đảm bảo đủ độ dài
        while len(music) < len(voice):
            music += music

        # Chỉnh âm lượng nhạc nền
        db_reduction_during_speech = 20 * math.log10(0.10)  # Giảm âm lượng nhạc nền xuống 10%
        db_reduction_without_speech = 20 * math.log10(0.14)  # Giảm âm lượng nhạc nền xuống 14%

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
            adjusted_music = adjusted_music.overlay(segment, position=start)

            current_position = end

        # Chèn nhạc nền sau đoạn giọng nói cuối cùng (nếu có)
        if current_position < len(voice):
            segment = music[current_position:].apply_gain(db_reduction_without_speech).fade_in(fade_duration // 2)
            adjusted_music = adjusted_music.overlay(segment, position=current_position)

        # Thêm giọng nói vào nhạc nền đã điều chỉnh
        combined = adjusted_music.overlay(voice, loop=False)

        output_wav_path = f'media/{video_id}/cache1.wav'
        
        # Xuất file âm thanh kết hợp
        combined.export(output_wav_path, format="wav")

        # Mã hóa âm thanh đầu ra thành định dạng MP3
        output_mp3_path = f'media/{video_id}/audio.wav'
        ffmpeg_encode_command = [
            'ffmpeg',
            '-i', output_wav_path,
            '-codec:a', 'libmp3lame',
            '-q:a', '2',
            output_mp3_path
        ]
        subprocess.run(ffmpeg_encode_command, check=True)
        return True
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    
def download_youtube_audio(url, output_file):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f"{output_file}",  # Định dạng tên file đầu ra
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',  # Chất lượng âm thanh
        }],
        'noplaylist': True,  # Không tải playlist, chỉ tải video đầu tiên
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        print(f"Tải âm thanh từ: {url}")
        ydl.download([url])

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

def get_audio_duration(file_path):
    try:
        # Gọi lệnh ffprobe để lấy thông tin về file âm thanh
        cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file_path]
        duration = subprocess.check_output(cmd, stderr=subprocess.STDOUT).strip()
        return float(duration)
    except Exception as e:
        print(f"Lỗi khi lấy thông tin từ file âm thanh: {e}")
        return None

def format_time(seconds):
    """Chuyển đổi thời gian từ giây thành định dạng hh:mm:ss.sss"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02}:{minutes:02}:{secs:06.3f}"

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

def translate_text(text, src_lang='auto', dest_lang='en'):
    translator = Translator()
    translation = translator.translate(text, src=src_lang, dest=dest_lang)
    return translation.text

def find_keywords(text, num_keywords=5):
    # Tokenize the text
    tokens = word_tokenize(text)
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word.lower() not in stop_words]
    # Compute the frequency distribution
    freq_dist = FreqDist(filtered_tokens)
    # Get the most common keywords
    keywords = [word for word, freq in freq_dist.most_common(num_keywords)]
    return keywords

def search_pixabay_videos(api_key, query, min_duration):
    filtered_videos = []
    for page in range(1,2):
        url = f"https://pixabay.com/api/videos/?key={api_key}&q={query}&per_page=200&page={page}"
        print(url)
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            for item in data['hits']:
                for video in item['videos'].values():
                    if video['height'] == 1080 and item['duration'] >= min_duration:
                        filtered_videos.append(video['url'])
    return filtered_videos

def get_video_random(data,duration,input_text,file_name):
    translated_text = translate_text(input_text)
    # Find the main keywords in the translated sentence
    keywords = find_keywords(translated_text)
    # Tìm video từ Pixabay
    api_key = "38396855-7183824f50d61fd232c569758" 

    list_url = []
    for keyword in keywords:
        result = search_pixabay_videos(api_key, keyword, duration)
        list_url.extend(result)
    list_url.extend(result)

    video_id = data.get('video_id')
    choice = random.choice(list_url)


    path = f'media/{video_id}/videodownload'
    # Tạo thư mục nếu chưa tồn tại
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    
    response = requests.get(choice, stream=True)
    if response.status_code == 200:
        video_path = f'media/{video_id}/videodownload/{file_name}.mp4'
        with open(video_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
        return video_path
# lấy thời gian của các file srt
def extract_frame_times(srt_content):
    time_pattern = re.compile(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})')
    matches = time_pattern.findall(srt_content)
    return matches

def download_and_read_srt(data, video_id):
    if data.get('file-srt'):
        max_retries = 30
        retries = 0
        srt_url = data.get('file-srt')  # URL của tệp SRT
        url = f'{SERVER}{srt_url}'
        while retries < max_retries:
            try:
                response = requests.get(url, stream=True)
                if response.status_code == 200:
                    os.makedirs(f'media/{video_id}', exist_ok=True)
                    srt_path = f'media/{video_id}/cache.srt'
                    with open(srt_path, 'wb') as file:
                        for chunk in response.iter_content(chunk_size=1024):
                            if chunk:  # Lọc bỏ các keep-alive chunks mới
                                file.write(chunk)
                    print("Tải xuống thành công.")
                    
                    # Đọc nội dung tệp SRT
                    with open(srt_path, 'r', encoding='utf-8') as file:
                        srt_content = file.read()
                    print("Nội dung của tệp SRT đã được tải và đọc thành công.")
                    
                    # Trích xuất thời gian các khung trong tệp SRT
                    frame_times = extract_frame_times(srt_content)
                    print("Thời gian của các khung trong tệp SRT:")
                    for start, end in frame_times:
                        print(f"Bắt đầu: {start}, Kết thúc: {end}")
                    
                    return frame_times
                else:
                    print(f"Lỗi {response.status_code}: Không thể tải xuống tệp.")
            except requests.RequestException as e:
                print(f"Lỗi tải xuống: {e}")

            retries += 1
            print(f"Thử lại {retries}/{max_retries}")
            time.sleep(5)  # Chờ một khoảng thời gian trước khi thử lại

        print("Không thể tải xuống tệp sau nhiều lần thử.")
        return []
    
def convert_to_seconds(time_str):
    time_format = '%H:%M:%S,%f'
    dt = datetime.strptime(time_str, time_format)
    delta = timedelta(hours=dt.hour, minutes=dt.minute, seconds=dt.second, microseconds=dt.microsecond)
    return delta.total_seconds()

def create_video(data, task_id, worker_id):
    try:
        list_video = []
        video_id = data.get('video_id')
        text  = data.get('text_content')
        list_video = []
        create_or_reset_directory(f'media/{video_id}/video')
        processed_entries = 0
        total_entries = len(json.loads(text))
        if data.get('file-srt'):
            data_sub = download_and_read_srt(data, video_id)
            if len(data_sub) == 0:
                return False
            if len(data_sub) != total_entries:
                return False
            
        for i,iteam in enumerate(json.loads(text)):
            if data.get('file-srt'):
                start_time, end_time = data_sub[i]
                duration = convert_to_seconds(end_time) - convert_to_seconds(start_time)
            else:
                duration = get_audio_duration(f'media/{video_id}/voice/{iteam["id"]}.wav')

            out_file = f'media/{video_id}/video/{iteam["id"]}.mp4'

            files = [f for f in os.listdir('video') if os.path.isfile(os.path.join('video', f))]
            file = get_filename_from_url(iteam['url_video'])
            if file == 'no-image-available.png' or iteam['url_video'] == '':
                while True:
                    try:
                        random_file = random.choice(files)
                        video_path = os.path.join('video', random_file)
                        if os.path.exists(video_path):
                            video_duration = get_video_duration(video_path)
                            print(f"Duration: {video_duration},{duration}")
                            if random_file not in list_video and duration < video_duration:
                                list_video.append(random_file)
                                break
                        else:
                            print(f"File not found: {video_path}")
                    except Exception as e:
                        print(f"Error processing file {random_file}: {e}")
                cut_and_scale_video_random(video_path,out_file, duration, 1920, 1080, 'video_screen')

            else:
                randoom_choice = random.choice([True, False])
                image_file = f'media/{video_id}/image/{file}'
                if randoom_choice:
                    image_to_video_zoom_in(image_file, out_file, duration, 1920, 1080, 'video_screen')
                else:
                    image_to_video_zoom_out(image_file, out_file, duration, 1920, 1080, 'video_screen')
            processed_entries += 1
            percent_complete = (processed_entries / total_entries) * 100
            update_status_video(f"Đang Render : Đang tạo video {percent_complete:.2f}%", data['video_id'], task_id, worker_id)
        return True  
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def create_video_lines(data, task_id, worker_id, max_retries=5):
    for attempt in range(max_retries):
        if create_video(data, task_id, worker_id):
            print(f"Video creation succeeded on attempt {attempt + 1}")
            return True
        else:
            print(f"Attempt {attempt + 1} failed, retrying...")
            time.sleep(1)  # Chờ một chút trước khi thử lại
    print("Max retries reached, video creation failed.")
    return False

def get_random_video_from_directory(directory_path):
    video_files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
    return os.path.join(directory_path, random.choice(video_files))

def image_to_video_zoom_out(input_image, output_video, duration, scale_width, scale_height, overlay_video):
    is_overlay_video = random.choice([True, False])
    base_video = get_random_video_from_directory(overlay_video)
    time_video = format_time(duration)
    if is_overlay_video:
        ffmpeg_command = [
            'ffmpeg',
            '-loop', '1',
            '-framerate','24',
            '-i', input_image,
            '-i', base_video,
            '-filter_complex',
            f"[0:v]format=yuv420p,scale=8000:-1,zoompan=z='zoom+0.001':x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):d={duration}*60:s={scale_width}x{scale_height}:fps=60[bg];[1:v]scale={scale_width}:{scale_height}[overlay];[bg][overlay]overlay[outv]",
            '-map', '[outv]',
            '-t', time_video,
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-y',  # Overwrite output file if exists
            output_video
        ]

    else:
        ffmpeg_command = [
        'ffmpeg',
        '-loop', '1',
        '-framerate','24',
        '-i', input_image,
        '-vf',
        f"format=yuv420p,scale=8000:-1,zoompan=z='zoom+0.001':x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):d={duration}*60:s={scale_width}x{scale_height}:fps=60",
        '-t', time_video,
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-y',  # Overwrite output file if exists
        output_video
    ]
    try:
        # Chạy lệnh FFmpeg
        subprocess.run(ffmpeg_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"lỗi chạy FFMPEG {e}")

def image_to_video_zoom_in(input_image, output_video, duration, scale_width, scale_height, overlay_video):
    is_overlay_video = random.choice([True, False])
    base_video = get_random_video_from_directory(overlay_video)
    time_video = format_time(duration)
    if is_overlay_video:
        ffmpeg_command = [
            'ffmpeg',
            '-loop', '1',
            '-framerate','24',
            '-i', input_image,
            '-i', base_video,
            '-filter_complex',
            f"[0:v]format=yuv420p,scale=8000:-1,zoompan=z='zoom+0.001':x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):d={duration}*60:s={scale_width}x{scale_height}:fps=60[bg];[1:v]scale={scale_width}:{scale_height}[overlay];[bg][overlay]overlay[outv]",
            '-map', '[outv]',
            '-r', '30',
            '-t', time_video,
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-y',  # Overwrite output file if exists
            output_video
        ]

    else:
        ffmpeg_command = [
        'ffmpeg',
        '-loop', '1',
        '-framerate','60',
        '-i', input_image,
        '-vf',
        f"format=yuv420p,scale=8000:-1,scale=8000:-1,zoompan=z='zoom+0.001':x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):d={duration}*60:s={scale_width}x{scale_height}:fps=60",
        '-t', time_video,
        '-r', '30',
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-y',  # Overwrite output file if exists
        output_video
    ]
    try:
        # Chạy lệnh FFmpeg
        subprocess.run(ffmpeg_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"lỗi chạy FFMPEG {e}")

def download_audio(data, task_id, worker_id):
    try:
        language = data.get('language')
        video_id = data.get('video_id')
        text = data.get('text_content')

        text_entries = json.loads(text)
        total_entries = len(text_entries)
        processed_entries = 0
        if language == 'Japanese-VoiceVox':
            with open(f'media/{video_id}/input_files.txt', 'w') as file:
                for text_entry in text_entries:
                    file_name = f'media/{video_id}/voice/{text_entry["id"]}.wav'
                    get_voice_japanese(data, text_entry['text'], file_name)
                    processed_entries += 1
                    percent_complete = (processed_entries / total_entries) * 100
                    update_status_video(f"Đang Render : Đang tạo giọng đọc {percent_complete:.2f}%", data['video_id'], task_id, worker_id)
                    file.write(f"file 'voice/{text_entry['id']}.wav'\n")

        elif language == 'Korea-TTS':
            with open(f'media/{video_id}/input_files.txt', 'w') as file:
                for text_entry in text_entries:
                    file_name = f'media/{video_id}/voice/{text_entry["id"]}.wav'
                    get_voice_korea(data, text_entry['text'], file_name)
                    processed_entries += 1
                    percent_complete = (processed_entries / total_entries) * 100
                    update_status_video(f"Đang Render : Đang tạo giọng đọc {percent_complete:.2f}%", data['video_id'], task_id, worker_id)
                    file.write(f"file 'voice/{text_entry['id']}.wav'\n")
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def download_audio_reup(data, task_id, worker_id):
    video_id = data.get('video_id')
    output_file = f'media/{video_id}/cache'
    url = data.get('url_video_youtube')

    # Hàm xử lý tiến trình tải
    def progress_hook(d):
        if d['status'] == 'downloading':
            percent = d['_percent_str'].strip()
            update_status_video(f"Đang Render : Đang tải audio {percent}", data['video_id'], task_id, worker_id)
        elif d['status'] == 'finished':
            update_status_video(f"Đang Render : Tải xong âm thanh ", data['video_id'], task_id, worker_id)

    # Cấu hình yt-dlp
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f"{output_file}",
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'noplaylist': True,
        'progress_hooks': [progress_hook],  # Thêm hàm xử lý tiến trình
    }

    with YoutubeDL(ydl_opts) as ydl:
        print(f"Tải âm thanh từ: {url}")
        ydl.download([url])
    return True

def format_timestamp(seconds):
    """Chuyển đổi thời gian từ giây thành định dạng SRT (hh:mm:ss,ms)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

def get_sub_audio(data, task_id, worker_id):
    video_id = data.get('video_id')
    audio_file = f'media/{video_id}/cache.wav'
    model = whisper.load_model('base')
    update_status_video("Đang Render : Đang lấy phụ đề video", data['video_id'], task_id, worker_id)
    output_srt = f"media/{video_id}/output.srt" 
    # Tạo thư mục nếu chưa tồn tại
    # Giải mã âm thanh và trích xuất phụ đề
    result = model.transcribe(audio_file)

    # Biến lưu trữ các đoạn phụ đề đã kết hợp
    combined_segments = []
    current_segment = None

    # Các dấu chấm kết thúc câu trong tiếng Anh và tiếng Nhật
    sentence_endings = ('.', '。', '．')

    for i, segment in enumerate(result['segments']):
        start = segment['start']
        end = segment['end']
        text = segment['text'].strip()

        if current_segment is None:
            # Khởi tạo đoạn phụ đề mới
            current_segment = {
                'start': start,
                'end': end,
                'text': text
            }
        else:
            if current_segment['text'].endswith(sentence_endings):
                # Nếu đoạn trước kết thúc bằng dấu chấm, thêm đoạn hiện tại vào danh sách
                combined_segments.append(current_segment)
                current_segment = {
                    'start': start,
                    'end': end,
                    'text': text
                }
            else:
                # Nếu đoạn trước không kết thúc bằng dấu chấm, gộp đoạn hiện tại với đoạn trước
                current_segment['end'] = end
                current_segment['text'] += ' ' + text

    # Thêm đoạn cuối cùng vào danh sách nếu có
    if current_segment:
        combined_segments.append(current_segment)

    # Đặt thời gian kết thúc của đoạn trước bằng thời gian bắt đầu của đoạn sau
    for i in range(len(combined_segments) - 1):
        combined_segments[i]['end'] = combined_segments[i + 1]['start']

    # Lấy thời gian kết thúc của file âm thanh
    audio_duration = librosa.get_duration(filename=audio_file)

    # Cập nhật thời gian kết thúc của đoạn phụ đề cuối cùng bằng thời gian kết thúc của file âm thanh
    combined_segments[-1]['end'] = audio_duration

    # Lưu kết quả dưới dạng file .srt
    with open(output_srt, "w") as f:
        for i, segment in enumerate(combined_segments):
            start = segment['start']
            end = segment['end']
            text = segment['text'].strip()

            # Ghi thông tin vào file SRT
            f.write(f"{i + 1}\n")  # Số thứ tự đoạn phụ đề
            f.write(f"{format_timestamp(start)} --> {format_timestamp(end)}\n")  # Thời gian bắt đầu và kết thúc
            f.write(f"{text}\n")  # Nội dung phụ đề
    return True

async def text_to_speech(text, voice, output_file):
    communicate = edge_tts.Communicate(text=text, voice=voice)
    await communicate.save(output_file)

def get_voice_korea(data, text, file_name):
    directory = os.path.dirname(file_name)
    name_langue = data.get('style')
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    asyncio.run(text_to_speech(text,name_langue, file_name))

def get_voice_japanese(data, text, file_name):
    try:
        # voice_id = data.get('voice_id')
        # url_query = f"http://127.0.0.1:50021/audio_query?speaker={voice_id}"
        # response_query = requests.post(url_query, params={'text': text})
        # response_query.raise_for_status()  # Kiểm tra mã trạng thái HTTP
        
        # query_json = response_query.json()

        # # Thay đổi giá trị speedScale trong tệp JSON
        # query_json["speedScale"] = 1.0

        # # Gửi yêu cầu POST để tạo tệp âm thanh với tốc độ đã thay đổi
        # url_synthesis = f"http://127.0.0.1:50021/synthesis?speaker={voice_id}"
        # headers = {"Content-Type": "application/json"}
        # response_synthesis = requests.post(url_synthesis, headers=headers, json=query_json)
        # response_synthesis.raise_for_status()  # Kiểm tra mã trạng thái HTTP

        # # Tạo thư mục nếu chưa tồn tại
        # directory = os.path.dirname(file_name)
        # if not os.path.exists(directory):
        #     os.makedirs(directory, exist_ok=True)

        # # Ghi nội dung phản hồi vào tệp
        # with open(file_name, 'wb') as f:
        #     f.write(response_synthesis.content)

        data = {
            "voice_id":  data.get('voice_id'),
            "action": "get-audio-voicevox",
            "text_voice": text,
            "secret_key": "ugz6iXZ.fM8+9sS}uleGtIb,wuQN^1J%EvnMBeW5#+CYX_ej&%"
        }

        url = f'{SERVER}/api/'

        response = requests.post(url, json=data)

        with open(file_name, 'wb') as f:
            file.write(response.content)
        return True
    except Exception as e:
        return False

def get_filename_from_url(url):
    parsed_url = urllib.parse.urlparse(url)
    path = parsed_url.path
    filename = path.split('/')[-1]
    return filename

def download_image(data, task_id, worker_id):
    video_id = data.get('video_id')
    update_status_video(f"Đang Render : Bắt đầu tải xuống hình ảnh", video_id, task_id, worker_id)

    local_directory = os.path.join('media', str(video_id), 'image')
    os.makedirs(local_directory, exist_ok=True)

    success = True  # Biến để theo dõi trạng thái tải xuống
    images_str = data.get('images')
    if not images_str:
        return True
    
    for image in json.loads(data.get('images')):
        url = f"{SERVER}/{image}"
        image_downloaded = False
        for attempt in range(30):
            try:
                response = requests.get(url, stream=True)
                if response.status_code == 200:
                    file_path = os.path.join(local_directory, get_filename_from_url(url))
                    with open(file_path, 'wb') as file:
                        for chunk in response.iter_content(1024):
                            file.write(chunk)
                    image_downloaded = True
                    update_status_video(f"Đang Render : Tải xuống hình ảnh thành công", video_id, task_id, worker_id)
                    break
                else:
                    pass
            except requests.RequestException as e:
                pass
            except Exception as e:
                pass
            time.sleep(1)
        # Nếu không tải được hình ảnh sau 30 lần thử, thay đổi trạng thái thành False
        if not image_downloaded:
            success = False
            update_status_video(f"Đang Render : Không thể tải xuống hình ảnh", video_id, task_id, worker_id)
    return success

def create_or_reset_directory(directory_path):
    try:
        # Kiểm tra xem thư mục có tồn tại hay không
        if os.path.exists(directory_path):
            # Kiểm tra xem thư mục có trống hay không
            if os.listdir(directory_path):
                # Nếu không trống, xóa thư mục và toàn bộ nội dung bên trong
                shutil.rmtree(directory_path)
                print(f"Đã xóa thư mục '{directory_path}' và toàn bộ nội dung.")
            else:
                # Nếu trống, chỉ xóa thư mục
                os.rmdir(directory_path)
                print(f"Đã xóa thư mục trống '{directory_path}'.")
        # Tạo lại thư mục
        os.makedirs(directory_path)
        return True
    except Exception as e:
        print(f"Lỗi: {e}")
        return False

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

def create_video_reup_url(data, task_id, worker_id):
    video_id = data.get('video_id')
    srt_path = f'media/{video_id}/output.srt'
    create_or_reset_directory(f'media/{video_id}/video')
    try:
        with open(srt_path, 'r', encoding='utf-8') as file:
            srt_content = file.read()
        subtitles = extract_subtitles(srt_content)
        list_video = []
        processed_entries = 0
        for i,iteam in enumerate(subtitles):
            duration = convert_to_seconds(iteam['end_time']) - convert_to_seconds(iteam['start_time'])
            out_file = f'media/{video_id}/video/{iteam["index"]}.mp4'
            files = [f for f in os.listdir('video') if os.path.isfile(os.path.join('video', f))]
            while True:
                try:
                    random_file = random.choice(files)
                    video_path = os.path.join('video', random_file)
                    if os.path.exists(video_path):
                        video_duration = get_video_duration(video_path)
                        print(f"Duration: {video_duration},{duration}")
                        if random_file not in list_video and duration < video_duration:
                            list_video.append(random_file)
                            break
                    else:
                        print(f"File not found: {video_path}")
                except Exception as e:
                    print(f"Error processing file {random_file}: {e}")
            cut_and_scale_video_random(video_path,out_file, duration, 1280, 720, 'video_screen')
            processed_entries += 1
            percent_complete = (processed_entries / len(subtitles)) * 100
            update_status_video(f"Đang Render : Đang tạo video {percent_complete:.2f}%", data['video_id'], task_id, worker_id)
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def create_video_url_lines(data, task_id, worker_id):
    for attempt in range(5):
        if create_video_reup_url(data, task_id, worker_id):
            print(f"Video creation succeeded on attempt {attempt + 1}")
            return True
        else:
            print(f"Attempt {attempt + 1} failed, retrying...")
            time.sleep(1)  # Chờ một chút trước khi thử lại
    print("Max retries reached, video creation failed.")
    return False

def create_subtitles_reup_url(data, task_id, worker_id):
    video_id = data.get('video_id')
    subtitle_file = f'media/{video_id}/subtitles.ass'
    color = data.get('font_color')
    color_backrought = data.get('color_backrought')
    color_border = data.get('stroke')
    font_text = data.get("font_name")
    font_size = data.get('font_size')
    stroke_text = data.get('stroke_size')
    text  = data.get('text_content')
    srt_path = f'media/{video_id}/output.srt'

    with open(subtitle_file, 'w', encoding='utf-8') as ass_file:
        # Viết header cho file ASS
        ass_file.write("[Script Info]\n")
        ass_file.write("Title: Subtitles\n")
        ass_file.write("ScriptType: v4.00+\n")
        ass_file.write("WrapStyle: 0\n")
        ass_file.write("ScaledBorderAndShadow: yes\n")
        ass_file.write("YCbCr Matrix: TV.601\n")
        ass_file.write(f"PlayResX: 1270\n")
        ass_file.write(f"PlayResY: 720\n\n")
        ass_file.write("[V4+ Styles]\n")
        ass_file.write("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n")
        ass_file.write(f"Style: Default,{font_text},{font_size},{color},{color_backrought},&H00000000,{color_border},0,0,0,0,100,100,0,0,1,{stroke_text},0,2,10,10,10,0\n\n")

        ass_file.write("[Events]\n")
        ass_file.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect,WrapStyle,Text\n")

        start_time = timedelta(0)
        with open(srt_path, 'r', encoding='utf-8') as file:
            srt_content = file.read()
        subtitles = extract_subtitles(srt_content)

        for i,iteam in enumerate(subtitles):
            ass_file.write(f"Dialogue: 0,{iteam['start_time'][:-1].replace(',', '.')},{iteam['end_time'][:-1].replace(',', '.')},Default,,0,0,0,,2,{get_text_lines(data,iteam['text'],width=1280)}\n")
        return True

def create_video_reup_urls(data, task_id, worker_id):
    video_id = data.get('video_id')
    name_video = data.get('name_video')
    # Tạo file subtitles.ass
    ass_file_path = f'media/{video_id}/subtitles.ass'

    # Tạo file input_files_video.txt
    input_files_video_path = f'media/{video_id}/input_files_video.txt'
    os.makedirs(os.path.dirname(input_files_video_path), exist_ok=True)

    srt_path = f'media/{video_id}/output.srt'
    with open(srt_path, 'r', encoding='utf-8') as file:
        srt_content = file.read()
    subtitles = extract_subtitles(srt_content)

    with open(input_files_video_path, 'w') as file:
        for item in subtitles:
            file.write(f"file 'video/{item['index']}.mp4'\n")

    audio_file = f'media/{video_id}/cache.wav'
    fonts_dir = r'apps/render/font'

    # Kiểm tra sự tồn tại của file audio
    if not os.path.exists(audio_file):
        print(f"Audio file not found: {audio_file}")
        return False
    
    ffmpeg_command = [
        'ffmpeg',
        '-f', 'concat',
        '-safe', '0',
        '-i', input_files_video_path,
        '-i', audio_file,
        '-vf', f"subtitles={ass_file_path}:fontsdir={fonts_dir}",
        '-c:v', 'libx264',
        '-map', '0:v',
        '-map', '1:a',
        '-y',
        f"media/{video_id}/{name_video}.mp4"
    ]

    try:
        result = subprocess.run(ffmpeg_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except subprocess.CalledProcessError as e:
        print(f"ffmpeg failed with error: {e.stderr}")
        return False
    return True


def update_info_video(data, task_id, worker_id):

    video_url  = data.get('url_video_youtube')

    yt = YouTube(video_url)

    title = yt.title
    thumbnail_url = yt.thumbnail_url

    video_id = data.get('video_id')
    url = f'{SERVER}/api/'
    update_status_video(f"Đang Render : Đang lấy thông tin video", video_id, task_id, worker_id)
    
    payload = {
        'video_id': str(video_id),
        'action': 'update-info-video',
        'secret_key': SECRET_KEY,
        'title': title,
        'thumbnail_url': thumbnail_url,  # Tên trường khác
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        print("Thông tin video đã được cập nhật thành công.")
        return True
    else:
        print(f"Lỗi cập nhật thông tin video: {response.status_code}")
        return False



@shared_task(queue='check_worker_status')
def check_worker_status():
    inspector = Celery('core').control.inspect()
    active_workers = inspector.active() or {}
    active_worker_hostnames = set(active_workers.keys())
    videos_in_progress = VideoRender.objects.filter(status_video__in=["Đang Render", "Đang Chờ Render"])
    for video in videos_in_progress:
        if video.worker_id not in active_worker_hostnames:
            video.status_video = f'Lỗi Render: Worker {video.worker_id} không hoạt động'
            video.save()
    print("Worker status checked successfully.")

@signals.task_revoked.connect
def task_revoked_handler(sender, request, terminated, signum, expired, **kw):
    video_id = request.args[0].get('video_id')
    task_id = request.id
    worker_id = "None"
    update_status_video("Render Lỗi : Dừng render", video_id, task_id, worker_id)

def update_status_video(status_video,video_id,task_id,worker_id):
    data = {
        'video_id': video_id,
        'status': status_video,
        'task_id': task_id,
        'worker_id': worker_id,
    }
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'public',  # Tên nhóm mà bạn muốn gửi thông điệp đến
        {
            'type': 'render_status',  # Loại thông điệp
            'data': data,
        }
    )