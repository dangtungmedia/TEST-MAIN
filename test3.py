import os
import requests
import urllib

import edge_tts,random,subprocess
import asyncio,json,shutil
from pydub import AudioSegment
import nltk
from googletrans import Translator
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import math
from datetime import timedelta
from pydub import AudioSegment
from PIL import Image, ImageDraw, ImageFont

# Download the necessary NLTK data files
nltk.download('punkt')
nltk.download('stopwords')

def render_video(data):
    video_id = data.get('video_id')

    if not os.path.exists('media'):
        os.makedirs('media')
    create_or_reset_directory(f'media/{video_id}')

    download_image(data)

    download_voice(data)

    cread_video(data)

    create_input_file(data)

    cread_subtitles(data)

    create_input_file_video(data)


def get_filename_from_url(url):
    parsed_url = urllib.parse.urlparse(url)
    path = parsed_url.path
    filename = path.split('/')[-1]
    return filename

def cread_subtitles(data):
    video_id = data.get('video_id')
    subtitle_file = f'media/{video_id}/subtitles.ass'
    color = data.get('color')
    color_backrought = data.get('color_backrought')
    color_border = data.get('color_border')
    font_text = data.get("font_name")
    font_size = data.get('font_size')
    stroke_text = data.get('stroke_text')
    text  = data.get('text')
    font_name = os.path.basename(font_text).split('.')[0]

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
        ass_file.write(f"Style: Default,{font_name},{font_size},{color},{color_backrought},&H00000000,{color_border},0,0,0,0,100,100,0,0,1,{stroke_text},0,2,10,10,10,0\n\n")

        ass_file.write("[Events]\n")
        ass_file.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect,WrapStyle,Text\n")

        start_time = timedelta(0)
        for iteam in json.loads(text):
            # audio = AudioSegment.from_wav(f'media/{video.id}/voice/{iteam["id"]}.wav')
            duration = get_audio_duration(f'media/{video_id}/voice/{iteam["id"]}.wav')
            print(duration)
            duration_milliseconds = duration * 1000
            end_time = start_time + timedelta(milliseconds=duration_milliseconds)
            # end_time = start_time + duration
            # Viết phụ đề
            ass_file.write(f"Dialogue: 0,{format_timedelta_ass(start_time)},{format_timedelta_ass(end_time)},Default,,0,0,0,,2,{get_text_lines(data,iteam['text'])}\n")
            start_time = end_time

def get_text_lines(data,text):
    current_line = ""
    wrapped_text = ""
    font_text = data.get("font_name")
    font_size = data.get('font_size')
    font = ImageFont.truetype(font_text,font_size)
    img = Image.new('RGB', (1, 1), color='black')
    draw = ImageDraw.Draw(img)

    for char in text:
        test_line = current_line + char
        bbox = draw.textbbox((0, 0), test_line, font=font)
        text_width = bbox[2] - bbox[0]

        # Kiểm tra nếu thêm dấu câu vào dòng mới vẫn giữ cho chiều rộng trên 50%
        if text_width <= 1920:
            current_line = test_line
        else:
            # Nếu chiều rộng vượt quá giới hạn, tìm vị trí của dấu câu cuối cùng
            last_punctuation_index = find_last_punctuation_index(current_line)
            if last_punctuation_index != -1:
                text_1 = current_line[:last_punctuation_index + 1]
                text_2 = current_line[last_punctuation_index + 1:]

                bbox_1 = draw.textbbox((0, 0), text_1, font=font)
                text_width_1 = bbox_1[2] - bbox_1[0]

                if text_width_1 <= int(1920 / 2):
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

def get_audio_duration(file_path):
    try:
        # Gọi lệnh ffprobe để lấy thông tin về file âm thanh
        cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file_path]
        duration = subprocess.check_output(cmd, stderr=subprocess.STDOUT).strip()
        return float(duration)
    except Exception as e:
        print(f"Lỗi khi lấy thông tin từ file âm thanh: {e}")
        return None

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
    create_or_reset_directory(f'media/{video_id}/videodownload')
    choice = random.choice(list_url)
    
    response = requests.get(choice, stream=True)
    if response.status_code == 200:
        video_path = f'media/{video_id}/videodownload/{file_name}.mp4'
        with open(video_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)

        return video_path

# Get video free pik
def cread_video(data):
    list_video = []
    video_id = data.get('video_id')
    text  = data.get('text')
    create_or_reset_directory(f'media/{video_id}/video')
    for iteam in json.loads(text):
        duration = get_audio_duration(f'media/{video_id}/voice/{iteam["id"]}.wav')
        files = [f for f in os.listdir('video') if os.path.isfile(os.path.join('video', f))]
        out_file = f'media/{video_id}/video/{iteam["id"]}.mp4'
        if iteam['url_video'] == '':
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

            video_path = get_video_random(data,duration,iteam['text'],iteam['id'])
            cut_and_scale_video_random(video_path,out_file, duration, 1920, 1080, 'video_screen')
        else:
            randoom_choice = random.choice([True, False])
            file = get_filename_from_url(iteam['url_video'])
            image_file = f'media/{video_id}/image/{file}'
            if randoom_choice:
                image_to_video_zoom_in(image_file, out_file, duration, 1920, 1080, 'video_screen')
            else:
                image_to_video_zoom_out(image_file, out_file, duration, 1920, 1080, 'video_screen')

def image_to_video_zoom_out(input_image, output_video, duration, scale_width, scale_height, overlay_video):
    is_overlay_video = random.choice([True, False])
    base_video = get_random_video_from_directory(overlay_video)
    if is_overlay_video:
        ffmpeg_command = [
            'ffmpeg',
            '-loop', '1',
            '-framerate','60',
            '-i', input_image,
            '-i', base_video,
            '-filter_complex',
            f"[0:v]format=yuv420p,scale=8000:-1,zoompan=z='zoom+0.001':x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):d={duration}*60:s={scale_width}x{scale_height}:fps=60[bg];[1:v]scale={scale_width}:{scale_height}[overlay];[bg][overlay]overlay[outv]",
            '-map', '[outv]',
            '-t', str(duration),
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-y',  # Overwrite output file if exists
            output_video
        ]

    else:
        ffmpeg_command = [
        'ffmpeg',
        '-loop', '1',
        '-framerate','30',
        '-i', input_image,
        '-vf',
        f"format=yuv420p,scale=8000:-1,zoompan=z='zoom+0.001':x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):d={duration}*60:s={scale_width}x{scale_height}:fps=60",
        '-t', str(duration),
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
    if is_overlay_video:
        ffmpeg_command = [
            'ffmpeg',
            '-loop', '1',
            '-framerate','60',
            '-i', input_image,
            '-i', base_video,
            '-filter_complex',
            f"[0:v]format=yuv420p,scale=8000:-1,zoompan=z='zoom+0.001':x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):d={duration}*60:s={scale_width}x{scale_height}:fps=60[bg];[1:v]scale={scale_width}:{scale_height}[overlay];[bg][overlay]overlay[outv]",
            '-map', '[outv]',
            '-r', '30',
            '-t', str(duration),
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
        '-t', str(duration),
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

def create_input_file(data):
    fade_duration=2000
    video_id = data.get('video_id')
    ffmpeg_command = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', f'media/{video_id}/input_files.txt',
            '-c', 'copy',
            f'media/{video_id}/cache.wav'
        ]
        # Chạy lệnh FFmpeg
    subprocess.run(ffmpeg_command, check=True)
    
    music_path = random.choice([f for f in os.listdir('music_background') if os.path.isfile(os.path.join('music_background', f))])
    music_path = os.path.join('music_background',music_path)

    voice = AudioSegment.from_file(f'media/{video_id}/cache.wav')
    music = AudioSegment.from_file(music_path)

    # Lặp lại nhạc nền để đảm bảo đủ độ dài
    while len(music) < len(voice):
        music += music
    
    # Chỉnh âm lượng nhạc nền
    db_reduction_during_speech = 20 * math.log10(0.10)  # Giảm âm lượng nhạc nền xuống 6%
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
    
    

    output_wav_path = f'media/{video_id}/chace1.wav'
    
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

def create_input_file_video(data):
    video_id = data.get('video_id')
    font_text = data.get("font_name")
    name_video = data.get('name_video')
    text = data.get('text')

    # Tạo file subtitles.ass
    ass_file_path = f'media/{video_id}/subtitles.ass'
    # Tạo file input_files_video.txt
    input_files_video_path = f'media/{video_id}/input_files_video.txt'
    os.makedirs(os.path.dirname(input_files_video_path), exist_ok=True)
    with open(input_files_video_path, 'w') as file:
        for item in json.loads(text):
            file.write(f"file 'video/{item['id']}.mp4'\n")

    audio_file = f'media/{video_id}/audio.wav'
    fonts_dir = os.path.dirname(font_text)

    # Kiểm tra sự tồn tại của file audio
    if not os.path.exists(audio_file):
        print(f"Audio file not found: {audio_file}")
        return
    
    ffmpeg_command = [
        'ffmpeg',
        '-f', 'concat',
        '-safe', '0',
        '-i', input_files_video_path,
        '-i', audio_file,
        '-vf', f"ass={ass_file_path}:fontsdir={fonts_dir}",
        '-c:v','libx264',
        '-map', '0:v', 
        '-map', '1:a', 
        '-y',
        f"media/{video_id}/{name_video}.mp4"
    ]

    try:
        result = subprocess.run(ffmpeg_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(f"ffmpeg output: {result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"ffmpeg failed with error: {e.stderr}")
        return
    
def download_voice(data):
    language = data.get('language')
    video_id = data.get('video_id')
    text  = data.get('text')
    if language == 'Japanese-VoiceVox':
        with open(f'media/{video_id}/input_files.txt', 'w') as file:
            for text in json.loads(text):
                file_name = f'media/{video_id}/voice/{text["id"]}.wav'
                get_voice_japanese(data,text['text'],file_name)
                print(f"Đã tải xuống giọng nói cho văn bản '{text['text']}' thành công.")
                file.write(f"file 'voice/{text['id']}.wav'\n")

    elif language == 'Korea-TTS':
        with open(f'media/{video_id}/input_files.txt', 'w') as file:
            for text in json.loads(text):
                file_name = f'media/{video_id}/voice/{text["id"]}.wav'
                get_voice_korea(data,text['text'],file_name)
                print(f"Đã tải xuống giọng nói cho văn bản '{text['text']}' thành công.")
                file.write(f"file 'voice/{text['id']}.wav'\n")

async def list_voices():
    voices_manager = await edge_tts.VoicesManager.create()
    voices = voices_manager.voices
    return voices

async def text_to_speech(text, voice, output_file):
    communicate = edge_tts.Communicate(text=text, voice=voice)
    await communicate.save(output_file)
    
def get_voice_korea(data, text, file_name):
    directory = os.path.dirname(file_name)
    namelanguage = data.get('voice_name')
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    
    voices = asyncio.run(list_voices())
    
    # Giả sử bạn muốn sử dụng giọng 'ko-KR-HyunsuNeural'
    selected_voice = next((voice for voice in voices if voice['ShortName'] == namelanguage), None)
    
    if selected_voice is None:
        raise ValueError("Giọng nói 'ko-KR-HyunsuNeural' không tồn tại.")
    
    asyncio.run(text_to_speech(text, selected_voice['ShortName'], file_name))

def get_voice_japanese(data, text, file_name):
    voice_id = data.get('voice_id')

    url_query = f"http://127.0.0.1:50021/audio_query?speaker={voice_id}"
    response_query = requests.post(url_query, params={'text': text})
    query_json = response_query.json()

    # Bước 3: Thay đổi giá trị speedScale trong tệp JSON
    query_json["speedScale"] = 1.0
    # Bước 4: Gửi yêu cầu POST để tạo tệp âm thanh với tốc độ đã thay đổi
    url_synthesis = f"http://127.0.0.1:50021/synthesis?speaker={voice_id}"
    headers = {"Content-Type": "application/json"}
    response_synthesis = requests.post(url_synthesis, headers=headers, json=query_json)

    # Tạo thư mục nếu chưa tồn tại
    directory = os.path.dirname(file_name)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    # Ghi nội dung phản hồi vào tệp
    with open(file_name, 'wb') as f:
        f.write(response_synthesis.content)
    
    print(f"Kết quả đã được lưu tại {file_name}")

def download_image(data):
    video_id = data.get('video_id')
    images = data.get('images')
    local_directory = os.path.join('media', str(video_id), 'image')
    os.makedirs(local_directory, exist_ok=True)

    for image in images:
        for attempt in range(30):
            try:
                response = requests.get(image, stream=True)
                if response.status_code == 200:
                    file_path = os.path.join(local_directory, get_filename_from_url(image))
                    with open(file_path, 'wb') as file:
                        for chunk in response.iter_content(1024):
                            file.write(chunk)
                    print(f"Tải xuống thành công: {file_path}")
                    break
                else:
                    print(f"Lỗi tải xuống, mã trạng thái: {response.status_code}. Thử lại lần {attempt + 1}")
            except Exception as e:
                print(f"Lỗi khi tải xuống: {e}. Thử lại lần {attempt + 1}")

def create_or_reset_directory(directory_path):
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
    print(f"Đã tạo lại thư mục '{directory_path}'.")

def format_time(seconds):
    """Chuyển đổi thời gian từ giây thành định dạng hh:mm:ss.sss"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02}:{minutes:02}:{secs:06.3f}"

def get_random_video_from_directory(directory_path):
    video_files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
    return os.path.join(directory_path, random.choice(video_files))


def cut_and_scale_video_random(input_video, output_video, duration, scale_width, scale_height, overlay_video):
    video_length = get_video_duration(input_video)
    start_time = random.uniform(0, video_length - duration)
    end_time = start_time + duration
    start_time_str = format_time(start_time)
    end_time_str = format_time(end_time)
    base_video = get_random_video_from_directory(overlay_video)
    is_overlay_video = random.choice([True, False])
    
    if is_overlay_video:
        cmd = [
            "ffmpeg",
            "-ss", start_time_str,
            "-to", end_time_str,
            "-i", input_video,
            "-ss", start_time_str,
            "-to", end_time_str,
            "-i", base_video,
            '-framerate','30',
            "-filter_complex", f"[0:v]scale={scale_width}:{scale_height}[bg];[1:v]scale={scale_width}:{scale_height}[overlay_scaled];[bg][overlay_scaled]overlay[outv]",
            "-map", "[outv]",
            '-r', '30',
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            "-an",
            '-y',  # Overwrite output file if exists
            output_video
        ]

        
    else:
        cmd = [
            "ffmpeg",
            "-ss", start_time_str,
            "-to", end_time_str,
            "-i", input_video,
            "-vf", f"scale={scale_width}:{scale_height}",
            '-r', '30',
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            "-an",
            '-y',  # Overwrite output file if exists
            output_video
        ]
    try:
        # Chạy lệnh FFmpeg
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")



text = '[{"id":"1","text":"안녕하세요, 저는 미국 챈들러 시의 작은 마을에서 살고 있는 킨슬리라고 합니다. 1111","url_video":"https://s3-hcm5-r1.longvan.net/19425936-media/data/234/image/438271633_425260880366527_5894690682966802905_n.jpg?AWSAccessKeyId=AUQESQVFF01YMVGUPVF9&Signature=VUoi5kDmj0BOIfZiFp1wcJ1a2ZY%3D&Expires=4400032607"},{"id":"2","text":"제겐 정말 괴짜 같은 아빠가 있는데요,","url_video":""},{"id":"3","text":"아빠는 한국 브랜드인 삼성에서 돈을 받은 것도 아닌데,","url_video":"https://s3-hcm5-r1.longvan.net/19425936-media/data/234/image/438271633_425260880366527_5894690682966802905_n.jpg?AWSAccessKeyId=AUQESQVFF01YMVGUPVF9&Signature=VUoi5kDmj0BOIfZiFp1wcJ1a2ZY%3D&Expires=4400032607"},{"id":"4","text":"마을 이곳저곳에 삼성을 홍보하고 다니고 있고,","url_video":""},{"id":"5","text":"한국 기업의 제품이라면 일단 구매부터 해보는 등,","url_video":"https://s3-hcm5-r1.longvan.net/19425936-media/data/234/image/438271633_425260880366527_5894690682966802905_n.jpg?AWSAccessKeyId=AUQESQVFF01YMVGUPVF9&Signature=VUoi5kDmj0BOIfZiFp1wcJ1a2ZY%3D&Expires=4400032607"},{"id":"6","text":"남들이 봤을 때는 도통 이해할 수 없는 행동을 하시곤 했죠.","url_video":""}]'

image = ["https://s3-hcm5-r1.longvan.net/19425936-media/data/234/image/438271633_425260880366527_5894690682966802905_n.jpg?AWSAccessKeyId=AUQESQVFF01YMVGUPVF9&Signature=VUoi5kDmj0BOIfZiFp1wcJ1a2ZY%3D&Expires=4400032607"]

font_text = r"apps/static/assets/fonts/Korea/Sokcho Bada Dotum TTF.ttf"

data = {
    'video_id': 234,
    'name_video': 'PQKOBYZ98Q',
    'text': text,
    'images': image,
    'font_name': font_text,
    'font_size': 90,
    'color': '&H00FFFFFF&',
    'color_backrought': '&H00FFFFFF&',
    'color_border': '&H00000000&',
    'stroke_text': 2,
    'language': 'Korea-TTS',
    'voice_id': '1',
    'voice_name': 'ko-KR-SunHiNeural',
}

# download_image(data)

# download_voice(data)

# cread_video(data)

# create_input_file(data)

# cread_subtitles(data)

# create_input_file_video(data)

render_video(data)

