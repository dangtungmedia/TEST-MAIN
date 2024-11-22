
    
import os
from celery import shared_task, Celery
import os, shutil, urllib
import time
import requests
import json
from PIL import Image, ImageDraw, ImageFont
import asyncio
import math
import urllib
import edge_tts, random, subprocess
import asyncio, json, shutil
from googletrans import Translator
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
import math
from datetime import timedelta, datetime
from requests_toolbelt.multipart.encoder import MultipartEncoder, MultipartEncoderMonitor
import re
from datetime import datetime, timedelta
import re
import yt_dlp
import decimal
import os
import random, subprocess
import decimal
from proglog import ProgressBarLogger
from tqdm import tqdm
from celery.signals import task_failure,task_revoked
from concurrent.futures import ThreadPoolExecutor, as_completed

import os
from dotenv import load_dotenv

# Nạp biến môi trường từ file .env
load_dotenv()

SECRET_KEY=os.environ.get('SECRET_KEY')
SERVER=os.environ.get('SERVER')
ACCESS_TOKEN = None


def delete_directory(video_id):
    directory_path = f'media/{video_id}'
    
    # Kiểm tra nếu thư mục tồn tại
    if os.path.exists(directory_path):
        # Kiểm tra xem thư mục có trống không
        if not os.listdir(directory_path):
            try:
                # Nếu thư mục trống, dùng os.rmdir để xóa
                os.rmdir(directory_path)
                print(f"Đã xóa thư mục trống: {directory_path}")
            except Exception as e:
                print(f"Lỗi khi xóa thư mục {directory_path}: {e}")
        else:
            try:
                # Nếu thư mục không trống, dùng shutil.rmtree để xóa toàn bộ
                shutil.rmtree(directory_path)
                print(f"Đã xóa thư mục cùng với các tệp: {directory_path}")
            except Exception as e:
                print(f"Lỗi khi xóa thư mục {directory_path}: {e}")
    else:
        print(f"Thư mục {directory_path} không tồn tại.")

# Xử lý khi task gặp lỗi
@task_failure.connect
def task_failure_handler(sender, task_id, exception, args, kwargs, traceback, einfo, **kw):
    video_id = args[0].get('video_id')
    worker_id = "None"
    update_status_video("Render Lỗi : Quá Thời gian render videos", video_id, task_id, worker_id)
    delete_directory(video_id)
    
# Xử lý khi task bị hủy
@task_revoked.connect
def clean_up_on_revoke(sender, request, terminated, signum, expired, **kw):
    task_id = request.id
    print(f"Task {task_id} bị hủy.")
    if request.args:
        video_id = request.args[0].get('video_id')
        delete_directory(video_id)
    else:
        print(f"Không thể tìm thấy video_id cho task {task_id} vì không có args.")


@shared_task(bind=True, priority=0,name='render_video',time_limit=14200,queue='render_video_content')
def render_video(self, data):
    task_id = render_video.request.id
    worker_id = render_video.request.hostname  # Lưu worker ID
    video_id = data.get('video_id')
    update_status_video("Đang Render : Đang lấy thông tin video render", data['video_id'], task_id, worker_id)
    success = create_or_reset_directory(f'media/{video_id}')
    if not success:
        shutil.rmtree(f'media/{video_id}')
        return

    success = cread_video(data, task_id, worker_id)
    if not success:
        # shutil.rmtree(f'media/{video_id}')
        return

    success = upload_video(data, task_id, worker_id)
    if not success:
        # shutil.rmtree(f'media/{video_id}')
        return
    update_status_video(f"Render Thành Công : Đang Chờ Upload lên Kênh", data['video_id'], task_id, worker_id)

class UploadProgress:
    def __init__(self, data, task_id, worker_id):
        self.last_printed_percent = 0
        self.data = data
        self.task_id = task_id
        self.worker_id = worker_id

    def progress_callback(self, monitor):
        # Calculate percentage uploaded
        percent_complete = (monitor.bytes_read / monitor.len) * 100
        # Check if the percentage has increased by at least 1%
        if int(percent_complete) > self.last_printed_percent:
            self.last_printed_percent = percent_complete
            # Print the percentage of upload completed
            print(f"Uploaded: {self.last_printed_percent}%")
            update_status_video(f"Đang Render : Đang Upload File Lên Server {self.last_printed_percent:.2f}%", self.data.get('video_id'), self.task_id, self.worker_id)

def upload_video(data, task_id, worker_id):
    video_id = data.get('video_id')
    name_video = data.get('name_video')
    video_path = f'media/{video_id}/{name_video}.mp4'
    url = f'{SERVER}/api/'

    update_status_video(f"Đang Render : Đang Upload File Lên Server", video_id, task_id, worker_id)
    
    payload = {
        'video_id': str(video_id),
        'action': 'upload',
        'secret_key': SECRET_KEY
    }

    try:
        with open(video_path, 'rb') as video_file:
            # Prepare the payload with the file and other fields
            encoder = MultipartEncoder(
                fields={
                    'video_id': str(payload['video_id']),
                    'action': payload['action'],
                    'secret_key': payload['secret_key'],
                    'file': (os.path.basename(video_path), video_file, 'application/octet-stream')
                }
            )
            
            # Create an instance of the UploadProgress class
            progress = UploadProgress(data, task_id, worker_id)
            
            # Create a monitor to use with the request
            monitor = MultipartEncoderMonitor(encoder, progress.progress_callback)
            
            # Make the POST request to upload the video with streaming data
            response = requests.post(
                url,
                data=monitor,
                headers={'Content-Type': monitor.content_type}
            )
        
        # Check if the request was successful
        if response.status_code == 200:
            print("\nUpload successful!")
            print("Response:", response.json())  # Print the response JSON for confirmation
            shutil.rmtree(f'media/{video_id}')
            return True
        else:
            print(f"\nUpload failed with status code: {response.status_code}")
            print("Response:", response.text)
            return False

    except FileNotFoundError:
        print(f"Error: The file {video_path} was not found.")
        return False
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False





def get_voice_japanese(data, text, file_name):
    """Hàm chuyển văn bản thành giọng nói tiếng Nhật với VoiceVox, bao gồm chức năng thử lại khi gặp lỗi."""
    directory = os.path.dirname(file_name)
    
    voice_id = data.get('voice_id')
    success = False
    attempt = 0
    
    while not success and attempt < 10:
        try:
            # Tạo audio query với VoiceVox
            url_query = f"http://voicevox:50021/audio_query?speaker={voice_id}"
            response_query = requests.post(url_query, params={'text': text})
            response_query.raise_for_status()  # Kiểm tra mã trạng thái HTTP
            
            # Lấy JSON từ phản hồi và điều chỉnh tốc độ
            query_json = response_query.json()
            query_json["speedScale"] = 1.0  # Điều chỉnh tốc độ

            # Yêu cầu tạo âm thanh
            url_synthesis = f"http://voicevox:50021/synthesis?speaker={voice_id}"
            headers = {"Content-Type": "application/json"}
            response_synthesis = requests.post(url_synthesis, headers=headers, json=query_json)
            response_synthesis.raise_for_status()  # Kiểm tra mã trạng thái HTTP

            # Ghi nội dung phản hồi vào tệp
            with open(file_name, 'wb') as f:
                f.write(response_synthesis.content)

            # Kiểm tra độ dài tệp âm thanh
            duration = get_audio_duration(file_name)
            if duration > 0:  # Đảm bảo rằng âm thanh có độ dài hợp lý
                success = True
                print(f"Tạo giọng nói thành công cho '{text}' tại {file_name}")
            else:
                print(f"Lỗi: Tệp âm thanh {file_name} không hợp lệ.")
        
        except requests.RequestException as e:
            print(f"Lỗi mạng khi gọi VoiceVox API: {e}. Thử lại...")
        except Exception as e:
            print(f"Lỗi không xác định: {e}. Thử lại...")

        attempt += 1
        if not success:
            time.sleep(1)  # Đợi 1 giây trước khi thử lại

    if not success:
        print(f"Không thể tạo giọng nói sau {attempt} lần thử.")
        return False
    return True

async def text_to_speech_async(text, voice, output_file):
    communicate = edge_tts.Communicate(text=text, voice=voice)
    await communicate.save(output_file)

def get_voice_korea(data, text, file_name):
    """Hàm xử lý TTS cho tiếng Hàn Quốc, tương tự get_voice_chat_gpt."""
    directory = os.path.dirname(file_name)
    name_langue = data.get('style')
    success = False
    attempt = 0
    
    while not success and attempt < 10:
        try:
            # Chạy text_to_speech dưới dạng không đồng bộ
            asyncio.run(text_to_speech_async(text, name_langue, file_name))
            
            # Kiểm tra độ dài tệp âm thanh
            duration = get_audio_duration(file_name)
            if duration > 0:  # Đảm bảo rằng âm thanh có độ dài hợp lý
                success = True
                print(f"Tạo giọng nói thành công cho '{text}' tại {file_name}")
            else:
                if os.path.exists(file_name):
                    os.remove(file_name)  # Xóa tệp nếu không hợp lệ
                print(f"Lỗi: Tệp âm thanh {file_name} không hợp lệ.")
        except Exception as e:
            print(f"Lỗi khi tạo giọng nói cho tiếng Hàn: {e}. Thử lại...")
        
        attempt += 1
        if not success:
            time.sleep(1)  # Đợi 1 giây trước khi thử lại
    
    if not success:
        print(f"Không thể tạo giọng nói sau {attempt} lần thử.")
        return False

def get_voice_chat_gpt(data, text, file_name):
    name_langue = data.get('style')
    url = "https://api.ttsopenai.com/api/v1/public/text-to-speech-stream"
    payload = {
        "model": "tts-1",
        "speed": 1,
        "input": text,
        "voice_id": name_langue
    }

    success = False
    attempt = 0
    
    while not success and attempt < 15:
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                with open(file_name, 'wb') as f:
                    f.write(response.content)
                
                # Kiểm tra độ dài của tệp âm thanh
                duration = get_audio_duration(file_name)
                if duration and duration > 0:
                    success = True
                    print(f"Tạo giọng nói thành công cho '{text}' tại {file_name}")
                else:
                    if os.path.exists(file_name):
                        os.remove(file_name)  # Xóa tệp nếu không hợp lệ
                    print(f"Lỗi: Tệp âm thanh {file_name} không hợp lệ.")
            else:
                print(f"Lỗi: API trả về trạng thái {response.status_code}. Thử lại...")
                
            attempt += 1
        except requests.RequestException as e:
            print(f"Lỗi mạng khi gọi API: {e}. Thử lại...")
            attempt += 1
            time.sleep(1)  # Đợi 1 giây trước khi thử lại
    
    if not success:
        print(f"Không thể tạo giọng nói sau {attempt} lần thử.")
    return success

def get_voice_chat_ai_human(data, text, file_name):
    headers = {
        "Authorization": "Bearer eyJhbGciOiJSUzI1NiJ9.eyJyb2xlIjoiUmp5ZWZuWWVHWl9idEZ2cUlqNDRNZyIsInNlcnZpY2VDb2RlIjoicmZUSUk2RURJZkE0dklvT3pxUUVqdyIsImVtYWlsIjoiV25YNGJiQTNGT1Qxdk5hbU9rMXhQU0Vwb1JDaEJLYmplM09TeDN5c19rdyIsIm1lbWJlcklkIjoiaXFCaHFFbTluTjhEUVdvUUdBalhXdyIsImlhdCI6MTcyOTU2OTYyNCwiZXhwIjoxNzI5NTc2ODI0fQ.JBiM-7532YiPAsaeCxo9Xg0jKRvO2LddpRJomTlTsdoSnHpLJEcXKUUBKez1gJd7RQJ1-YHWzMF6NgKiWIXc13JktWeL6XqtYLiIqOSglaWvJVMRgEmMuBmX6WpReh4nvnJZ3bils8X6Qnh3uqe9HKLtqLoi2K8EnrEw2aCpvSuf6_q8J8c9tyHuZNsQJQLbXoLEQLmIQRZnv0Eu91cE3IGs9694sIlrgD5pNkGJVqzdLFd0SRzq61SgBubAWGuY-Kk8vdypy-2QN8xCgoCzUPWs6LlLzLhlvzQJFaOF0WED2VBzg_hPgqgC_pxsxyLX0SdMXWv5giBUc0P84ler3w"
    }
    
    payload = {
        "model_name": data.get("style"),
        "emotion": "neutral",
        "language": "ko",
        "pitch": 10,
        "text": text,
        "speed": 10,
        "smart_words": "[[\"\",\"\"]]"
    }

    success = False
    attempt = 0
    
    while not success and attempt < 10:
        try:
            # Gửi yêu cầu đến API để lấy URL tệp âm thanh
            response = requests.post("https://aihumanstudio.ai/api/v1/TtsHumeloModel", headers=headers, json=payload)
            response.raise_for_status()  # Kiểm tra mã trạng thái HTTP
            
            response_json = response.json()
            tts_path = response_json.get('tts_path')
            
            if not tts_path:
                raise ValueError("Không nhận được đường dẫn tệp âm thanh từ API.")

            # Tải xuống tệp âm thanh từ URL trả về
            response_synthesis = requests.get(tts_path)
            response_synthesis.raise_for_status()  # Kiểm tra mã trạng thái HTTP

            # Lưu tệp âm thanh
            with open(file_name, 'wb') as f:
                f.write(response_synthesis.content)
            
            # Kiểm tra độ dài tệp âm thanh
            duration = get_audio_duration(file_name)
            if duration > 0:
                success = True
                print(f"Tạo giọng nói thành công cho '{text}' tại {file_name}")
            else:
                if os.path.exists(file_name):
                    os.remove(file_name)  # Xóa tệp nếu không hợp lệ
                print(f"Lỗi: Tệp âm thanh {file_name} không hợp lệ.")
        
        except requests.RequestException as e:
            print(f"Lỗi mạng khi gọi API AI Human Studio: {e}. Thử lại...")
        except Exception as e:
            print(f"Lỗi không xác định: {e}. Thử lại...")

        attempt += 1
        if not success:
            time.sleep(1)  # Đợi 1 giây trước khi thử lại

    if not success:
        print(f"Không thể tạo giọng nói sau {attempt} lần thử.")
        return False
    return True

def get_voice_super_voice(data, text, file_name):     
    success = False
    attempt = 0
    while not success and attempt < 10:
        try:
            url_voice_text = get_voice_text(text, data)
            if not url_voice_text:
                return False

            url_voice = get_audio_url(url_voice_text)
            if not url_voice:
                return False

            final_url = get_url_voice_succes(url_voice)
            if not final_url:
                return False
            
            response = requests.get(final_url)
            if response.status_code == 200:
                with open(file_name, 'wb') as f:
                    f.write(response.content)
                # Kiểm tra độ dài tệp âm thanh
                duration = get_audio_duration(file_name)
                if duration > 0:
                    success = True
                    print(f"Tạo giọng nói thành công cho '{text}' tại {file_name}")
                else:
                    if os.path.exists(file_name):
                        os.remove(file_name)
                    print(f"Lỗi: Tệp âm thanh {file_name} không hợp lệ.")
            else:
                print(f"Lỗi: API trả về trạng thái {response.status_code}. Thử lại...")
        except requests.RequestException as e:
            print(f"Lỗi mạng khi gọi API: {e}. Thử lại...")
        except Exception as e:
            print(f"Lỗi không xác định: {e}. Thử lại...")
            
        attempt += 1
        if not success:
            time.sleep(1)
    if not success:
        print(f"Không thể tạo giọng nói sau {attempt} lần thử.")
    return success


def get_url_voice_succes(url_voice):

    max_retries = 5  # Số lần thử lại tối đa
    retry_delay = 2  # Thời gian chờ giữa các lần thử (giây)

    for attempt in range(max_retries):
         # Làm mới token nếu cần
        if ACCESS_TOKEN is None:  # Nếu token chưa có, làm mới
            print("Refreshing ACCESS_TOKEN...")
            get_cookie("dangtungmedia@gmail.com", "@@Hien17987")

        if ACCESS_TOKEN is None:  # Nếu không lấy được token, dừng thử lại
            print("Unable to retrieve ACCESS_TOKEN. Exiting.")
            return None
        url = "url_voice" + '/cloudfront'
        headers = {
            'Authorization': f'Bearer {ACCESS_TOKEN}'
        }
            
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()['result']
            elif response.status_code == 401:  # Token hết hạn
                print("Unauthorized. Token may be expired. Refreshing token...")
                get_cookie("dangtungmedia@gmail.com", "@@Hien17987")
            else:
                print("API call failed with status code:", response.status_code)
                print("Response text:", response.text)
        except requests.RequestException as e:
            print("Error occurred during API request:", e)
        # Chờ trước khi thử lại
        time.sleep(retry_delay)
    
    return None     

def get_audio_url(url_voice_text):
    """Hàm lấy URL audio từ API."""
    max_retries = 5  # Số lần thử lại tối đa
    retry_delay = 2  # Thời gian chờ giữa các lần thử (giây)

    for attempt in range(max_retries):
        print(f"Attempt {attempt + 1} of {max_retries}.")

        # Làm mới token nếu cần
        if ACCESS_TOKEN is None:  # Nếu token chưa có, làm mới
            print("Refreshing ACCESS_TOKEN...")
            get_cookie("dangtungmedia@gmail.com", "@@Hien17987")

        if ACCESS_TOKEN is None:  # Nếu không lấy được token, dừng thử lại
            print("Unable to retrieve ACCESS_TOKEN. Exiting.")
            return None

        # Gửi yêu cầu POST đến API
        url = "https://typecast.ai/api/speak/batch/get"
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}"
        }
        try:
            response = requests.post(url, headers=headers, json=url_voice_text)

            print("Response status code:", response.status_code)

            # Xử lý phản hồi từ API
            if response.status_code == 200:
                try:
                    result = response.json().get("result", [])[0]
                    audio_url = result.get("audio", {}).get("url")
                    if audio_url:
                        print("Audio URL found:", audio_url)
                        return audio_url
                    else:
                        print("Không tìm thấy trường 'audio' trong phản hồi.")
                except (KeyError, IndexError, TypeError) as e:
                    print("Error parsing JSON response:", e)
            elif response.status_code == 401:  # Token hết hạn
                print("Unauthorized. Token may be expired. Refreshing token...")
                get_cookie("dangtungmedia@gmail.com", "@@Hien17987")
            else:
                print("API call failed with status code:", response.status_code)
                print("Response text:", response.text)

        except requests.RequestException as e:
            print("Error occurred during API request:", e)

        # Chờ trước khi thử lại
        time.sleep(retry_delay)

    print("Exceeded maximum retries. Unable to get audio URL.")
    return None


def get_voice_text(text, data):
    retry_count = 0
    max_retries = 3  # Giới hạn số lần thử lại

    while retry_count < max_retries:
        try:
            style_name_data = json.loads(data.get("style"))
            style_name_data[0]["text"] = text


            if ACCESS_TOKEN:
                get_cookie(os.environ.get('EMAIL'), os.environ.get('PASSWORD'))
            
            # Gửi yêu cầu POST
            url = 'https://typecast.ai/api/speak/batch/post'
            headers = {
                'Authorization': f'Bearer {ACCESS_TOKEN}',
                'Content-Type': 'application/json'
            }
            response = requests.post(url, headers=headers, json=style_name_data)

            # Nếu thành công, trả về dữ liệu
            if response.status_code == 200:
                return response.json().get("result", {}).get("speak_urls", [])
            
            # Nếu gặp lỗi unauthorized, tăng số lần thử lại
            elif response.status_code == 401:
                print("Token expired, refreshing token...")
                get_cookie("dangtungmedia@gmail.com", "@@Hien17987")
                retry_count += 1
            else:
                print("API call failed:", response.status_code)
                return False

        except Exception as e:
            print("Error:", e)
            retry_count += 1
    return False
  
# Hàm thử lại với decorator
def retry(retries=3, delay=2):
    """
    Decorator để tự động thử lại nếu hàm gặp lỗi.
    
    Args:
        retries (int): Số lần thử lại tối đa.
        delay (int): Thời gian chờ giữa các lần thử (giây).

    Returns:
        Kết quả trả về từ hàm nếu thành công, None nếu thất bại.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(1, retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Lỗi trong {func.__name__}, lần thử {attempt}: {e}")
                    if attempt < retries:
                        print(f"Thử lại sau {delay} giây...")
                        time.sleep(delay)
                    else:
                        print(f"{func.__name__} thất bại sau {retries} lần thử.")
                        return None
        return wrapper
    return decorator

@retry(retries=3, delay=2)
def active_token(access_token):
    """
    Lấy idToken từ access_token.
    """
    Params = {
        "key": "AIzaSyBJN3ZYdzTmjyQJ-9TdpikbsZDT9JUAYFk"
    }
    data = {
        "token": access_token,
        "returnSecureToken": True
    }
    response = requests.post(
        'https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken',
        params=Params,
        json=data
    )
    response.raise_for_status()
    return response.json()['idToken']

@retry(retries=3, delay=2)
def get_access_token(idToken):
    """
    Lấy access_token từ idToken.
    """
    data = {
        "token": idToken
    }
    response = requests.post(
        'https://typecast.ai/api/auth-fb/custom-token',
        json=data
    )
    response.raise_for_status()
    return response.json()["result"]['access_token']

@retry(retries=3, delay=2)
def login_data(email, password):
    """
    Lấy idToken bằng cách đăng nhập với email và password.
    """
    data = {
        "returnSecureToken": True,
        "email": email,
        "password": password,
        "clientType": "CLIENT_TYPE_WEB"
    }
    Params = {
        "key": "AIzaSyBJN3ZYdzTmjyQJ-9TdpikbsZDT9JUAYFk"
    }
    url = 'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword'
    response = requests.post(url, params=Params, json=data)
    response.raise_for_status()
    return response.json()['idToken']


def get_cookie(email, password, access_token=None):
    """
    Kết hợp các bước:
    1. Đăng nhập để lấy idToken nếu access_token không được cung cấp.
    2. Lấy idToken từ active_token nếu access_token có sẵn.
    3. Lấy access_token từ idToken và lưu vào biến toàn cục.

    Args:
        email (str): Email đăng nhập.
        password (str): Mật khẩu đăng nhập.
        access_token (str, optional): Access token nếu đã có sẵn.

    Returns:
        str: Access token (cookie) nếu thành công, None nếu thất bại.
    """
    global ACCESS_TOKEN  # Khai báo biến toàn cục
    try:
        if access_token:
            print("Sử dụng access_token để lấy idToken...")
            idToken = active_token(access_token)
        else:
            print("Đăng nhập bằng email và password để lấy idToken...")
            idToken = login_data(email, password)
        
        print("Lấy access_token từ idToken...")
        ACCESS_TOKEN = get_access_token(idToken)  # Lưu vào biến toàn cục

    except Exception as e:
        ACCESS_TOKEN = None
        print(f"Lỗi khi lấy cookie: {e}")


def process_voice_entry(data,text,language,path_audio, task_id,worker_id):
    """Hàm xử lý giọng nói cho từng trường hợp ngôn ngữ."""
    success = False
    # Xử lý ngôn ngữ tương ứng và kiểm tra kết quả tải
    if language == 'Japanese-VoiceVox':
        success = get_voice_japanese(data, text, path_audio)
    elif language == 'Korea-TTS':
        success = get_voice_korea(data, text, path_audio)
    elif language == 'VOICE GPT AI':
        success = get_voice_chat_gpt(data,text, path_audio)
    
    elif language == 'AI-HUMAN':
        success = get_voice_chat_ai_human(data,text, path_audio)
        
    elif language == 'SUPER VOICE':
        success = get_voice_super_voice(data,text, path_audio)

    return success



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


def get_random_video_from_directory(directory_path):
    video_files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
    return os.path.join(directory_path, random.choice(video_files))

def cut_and_scale_video_random(video_path,path_audio,path_video,scale_width, scale_height, overlay_video_dir):
    """Cắt video, thay đổi kích thước, thêm audio và chồng video trong một lệnh FFmpeg."""
    video_length = get_video_duration(video_path)
    duration = get_audio_duration(path_audio)
    start_time = random.uniform(0, video_length - duration)
    start_time_str = format_time(start_time)

    # Lấy video chồng nếu cần
    base_video = get_random_video_from_directory(overlay_video_dir)
    is_overlay_video = random.choice([True, False])

    try:
        if is_overlay_video and base_video:
            # Lệnh với overlay
            cmd = [
                "ffmpeg",
                "-ss", start_time_str,               # Thời gian bắt đầu cắt
                "-t", str(duration),                 # Thời lượng video
                "-i", video_path,                    # Video gốc
                "-ss", start_time_str,               # Thời gian bắt đầu cắt
                "-t", str(duration),                 # Thời lượng video
                "-i", base_video,                    # Video chồng
                "-i", path_audio,                    # Audio mới
                "-filter_complex",
                f"[0:v]scale={scale_width}:{scale_height}[bg];"  # Scale video gốc
                f"[1:v]scale={scale_width}:{scale_height}[overlay_scaled];"  # Scale video chồng
                f"[bg][overlay_scaled]overlay=format=auto,format=yuv420p[outv]",  # Overlay
                "-map", "[outv]",                    # Lấy video từ filter_complex
                "-map", "2:a",                       # Lấy audio từ file audio
                "-c:v", "libx264",                   # Codec video
                "-c:a", "aac",                       # Codec audio
                "-b:a", "192k",                      # Bitrate audio
                '-r', '24', 
                "-pix_fmt", "yuv420p",               # Đảm bảo tương thích
                "-shortest",                         # Đảm bảo audio không dài hơn video
                "-y",                                # Ghi đè file đầu ra
                path_video
            ]
        else:
            # Lệnh không overlay
            cmd = [
                "ffmpeg",
                "-ss", start_time_str,               # Thời gian bắt đầu cắt
                "-t", str(duration),                 # Thời lượng video
                "-i", video_path,                    # Video gốc
                "-i", path_audio,                    # Audio mới
                "-vf", f"scale={scale_width}:{scale_height}",  # Scale video
                "-map", "0:v",                       # Lấy video gốc
                "-map", "1:a",                       # Lấy audio từ file audio
                "-c:v", "libx264",                   # Codec video
                "-c:a", "aac",                       # Codec audio
                "-b:a", "192k",                      # Bitrate audio
                '-r', '24', 
                "-pix_fmt", "yuv420p",               # Đảm bảo tương thích
                "-shortest",                         # Đảm bảo audio không dài hơn video
                "-y",                                # Ghi đè file đầu ra
                path_video
            ]

        # Chạy lệnh FFmpeg
        subprocess.run(cmd, check=True)
        print(f"Video saved to: {path_video}")

    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

def get_filename_from_url(url):
    parsed_url = urllib.parse.urlparse(url)
    path = parsed_url.path
    filename = path.split('/')[-1]
    return filename

def image_to_video_zoom_out(image_file, path_audio, path_video,scale_width, scale_height, overlay_video):
    """Tạo video từ hình ảnh với hiệu ứng zoom-out và thêm âm thanh."""
    is_overlay_video = random.choice([True, False])
    duration = get_audio_duration(path_audio)
    base_video = get_random_video_from_directory(overlay_video)
    time_video = format_time(duration)

    if is_overlay_video and base_video:
        ffmpeg_command = [
            'ffmpeg',
            '-loop', '1',                                # Lặp hình ảnh
            '-framerate', '24',                          # Số khung hình mỗi giây
            '-i', image_file,                            # File hình ảnh đầu vào
            '-i', base_video,                            # Video overlay
            '-i', path_audio,                            # File âm thanh
            '-filter_complex',
            f"[0:v]format=yuv420p,scale=8000:-1,zoompan=z='zoom+0.001':x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):d={duration}*24:s={scale_width}x{scale_height}:fps=24[bg];"
            f"[1:v]scale={scale_width}:{scale_height}[overlay_scaled];"
            f"[bg][overlay_scaled]overlay=format=auto,format=yuv420p[outv]",
            '-map', '[outv]',                            # Lấy video đã xử lý
            '-map', '2:a',                               # Lấy âm thanh từ file audio
            '-t', time_video,                            # Đặt thời lượng video
            '-r', '24',                                  # Tốc độ khung hình đầu ra
            '-c:v', 'libx264',                           # Codec video
            '-c:a', 'aac',                               # Codec audio
            '-b:a', '192k',                              # Bitrate audio
            '-pix_fmt', 'yuv420p',                       # Định dạng pixel tương thích
            '-shortest',                                 # Đồng bộ độ dài video và audio
            '-y',                                        # Ghi đè file đầu ra nếu đã tồn tại
            path_video                                   # File đầu ra
        ]
    else:
        ffmpeg_command = [
            'ffmpeg',
            '-loop', '1',                                # Lặp hình ảnh
            '-framerate', '24',                          # Số khung hình mỗi giây
            '-i', image_file,                            # File hình ảnh đầu vào
            '-i', path_audio,                            # File âm thanh
            '-vf',
            f"format=yuv420p,scale=8000:-1,zoompan=z='zoom+0.001':x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):d={duration}*24:s={scale_width}x{scale_height}:fps=24",
            '-t', time_video,                            # Đặt thời lượng video
            '-r', '24',                                  # Tốc độ khung hình đầu ra
            '-c:v', 'libx264',                           # Codec video
            '-c:a', 'aac',                               # Codec audio
            '-b:a', '192k',                              # Bitrate audio
            '-pix_fmt', 'yuv420p',                       # Định dạng pixel tương thích
            '-shortest',                                 # Đồng bộ độ dài video và audio
            '-y',                                        # Ghi đè file đầu ra nếu đã tồn tại
            path_video                                   # File đầu ra
        ]

    try:
        # Chạy lệnh FFmpeg
        subprocess.run(ffmpeg_command, check=True)
        print(f"Video created successfully: {path_video}")
    except subprocess.CalledProcessError as e:
        print(f"Error running FFmpeg: {e}")


def image_to_video_zoom_in(image_file, path_audio, path_video, scale_width, scale_height, overlay_video):
    """Tạo video từ hình ảnh với hiệu ứng zoom-in và thêm âm thanh."""
    is_overlay_video = random.choice([True, False])
    base_video = get_random_video_from_directory(overlay_video)
    duration = get_audio_duration(path_audio)
    time_video = format_time(duration)

    if is_overlay_video and base_video:
        ffmpeg_command = [
            'ffmpeg',
            '-loop', '1',                                # Lặp hình ảnh
            '-framerate', '24',                          # Số khung hình mỗi giây
            '-i', image_file,                            # File hình ảnh đầu vào
            '-i', base_video,                            # Video overlay
            '-i', path_audio,                            # File âm thanh
            '-filter_complex',
            f"[0:v]format=yuv420p,scale=8000:-1,zoompan=z='zoom+0.005':x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):d={duration}*24:s={scale_width}x{scale_height}:fps=24[bg];"
            f"[1:v]scale={scale_width}:{scale_height}[overlay_scaled];"
            f"[bg][overlay_scaled]overlay=format=auto,format=yuv420p[outv]",
            '-map', '[outv]',                            # Lấy video đã xử lý
            '-map', '2:a',                               # Lấy âm thanh từ file audio
            '-t', time_video,                            # Đặt thời lượng video
            '-r', '24',                                  # Tốc độ khung hình đầu ra
            '-c:v', 'libx264',                           # Codec video
            '-c:a', 'aac',                               # Codec audio
            '-b:a', '192k',                              # Bitrate audio
            '-pix_fmt', 'yuv420p',                       # Định dạng pixel tương thích
            '-shortest',                                 # Đồng bộ độ dài video và audio
            '-y',                                        # Ghi đè file đầu ra nếu đã tồn tại
            path_video                                   # File đầu ra
        ]
    else:
        ffmpeg_command = [
            'ffmpeg',
            '-loop', '1',                                # Lặp hình ảnh
            '-framerate', '24',                          # Số khung hình mỗi giây
            '-i', image_file,                            # File hình ảnh đầu vào
            '-i', path_audio,                            # File âm thanh
            '-vf',
            f"format=yuv420p,scale=8000:-1,zoompan=z='zoom+0.005':x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):d={duration}*24:s={scale_width}x{scale_height}:fps=24",
            '-t', time_video,                            # Đặt thời lượng video
            '-r', '24',                                  # Tốc độ khung hình đầu ra
            '-c:v', 'libx264',                           # Codec video
            '-c:a', 'aac',                               # Codec audio
            '-b:a', '192k',                              # Bitrate audio
            '-pix_fmt', 'yuv420p',                       # Định dạng pixel tương thích
            '-shortest',                                 # Đồng bộ độ dài video và audio
            '-y',                                        # Ghi đè file đầu ra nếu đã tồn tại
            path_video                                   # File đầu ra
        ]

    try:
        # Chạy lệnh FFmpeg
        subprocess.run(ffmpeg_command, check=True)
        print(f"Video created successfully: {path_video}")
    except subprocess.CalledProcessError as e:
        print(f"Error running FFmpeg: {e}")


def find_last_punctuation_index(line):
    punctuation = "。、！？.,"  # Các dấu câu có thể xem xét
    last_punctuation_index = -1

    for i, char in enumerate(reversed(line)):
        if char in punctuation:
            last_punctuation_index = len(line) - i - 1
            break
    return last_punctuation_index


def get_text_lines(data, text,width=1920):
    current_line = ""
    wrapped_text = ""
    font = data['font_name']
    font_size = data.get('font_size')

    font = ImageFont.truetype(font,font_size)

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

def format_timedelta_ass(ms):
    # Định dạng thời gian cho ASS
    total_seconds = ms.total_seconds()
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int((seconds - int(seconds)) * 100)
    seconds = int(seconds)
    return "{:01}:{:02}:{:02}.{:02}".format(int(hours), int(minutes), seconds, milliseconds)


def process_entry(data, index, item, total_entries, video_id, task_id, worker_id):
    try:
        language = data.get('language')
        update_status_video(f"Đang Render: Đang tạo giọng đọc", video_id, task_id, worker_id)
        
        # Tạo giọng nói
        text = item["text"]
        path_audio = f'media/{video_id}/voice/{item["id"]}.wav'
        succes = process_voice_entry(data, text, language, path_audio, task_id, worker_id)
        if not succes:
            update_status_video(f"Render Lỗi: giọng đọc thất bại", video_id, task_id, worker_id)
            return False
        
        update_status_video(f"Đang Render: đã tạo xong giọng đọc", video_id, task_id, worker_id)
        # Tải hoặc xử lý video
        path_video = f'media/{video_id}/video/{item["id"]}.mp4'
        file = item.get('url_video')
        update_status_video(f"Đang Render: Đang Xử lý Video {item["id"]} ", video_id, task_id, worker_id)
        duration = get_audio_duration(path_audio)
        if file == 'no-image-available.png' or not file:
            max_retries = 10
            retries = 0
            while retries < max_retries:
                data_request = {
                    'secret_key': SECRET_KEY,
                    'action': 'get-video-backrought',
                    'task_id': task_id,
                    'worker_id': worker_id,
                    'list_video': os.listdir(f'media/{video_id}/video_backrought'),
                    'duration': duration,
                }
                url = f'{SERVER}/api/'
                response = requests.post(url, json=data_request)

                if response.status_code == 200:
                    filename = response.headers.get('Content-Disposition').split('filename=')[1].strip('"')
                    video_path = os.path.join(f'media/{video_id}/video_backrought', filename)
                    
                    # Lưu video tải về
                    with open(video_path, 'wb') as f:
                        f.write(response.content)

                    # Kiểm tra và thoát khỏi vòng lặp nếu tải thành công
                    if os.path.exists(video_path) and get_video_duration(video_path) >= duration:
                        cut_and_scale_video_random(video_path,path_audio, path_video,1920, 1080, 'video_screen')
                        break
                    else:
                        print("Video tải về không đạt độ dài yêu cầu.")
                else:
                    print(f"Lỗi {response.status_code}: Không thể tải xuống tệp từ API.")
                
                retries += 1
                print(f"Thử lại {retries}/{max_retries}")

            if retries == max_retries:
                print("Không thể tải video phù hợp sau nhiều lần thử.")
                return False  # Dừng lại nếu không thành công sau max_retries lần thử
        
        else:
            response = requests.get(file, stream=True, timeout=10)
            image_file = os.path.join(f'media/{video_id}/image', get_filename_from_url(file))

            if not os.path.exists(image_file):
                response = requests.get(file, stream=True, timeout=10)
                with open(image_file, 'wb') as f:
                    f.write(response.content)

            random_choice = random.choice([True, False])
            if random_choice:
                image_to_video_zoom_in(image_file, path_audio, path_video,1920, 1080, 'video_screen')
            else:
                image_to_video_zoom_out(image_file, path_audio, path_video,1920, 1080, 'video_screen')
        
        update_status_video(f"Đang Render: Đã xử lý xong video {item["id"]} ", video_id, task_id, worker_id)
        return True
    except Exception as e:
        print(f"Lỗi khi xử lý mục {index}: {e}")
        return False


def cread_video(data, task_id, worker_id):
    video_id = data.get('video_id')
    text = data.get('text_content')
    name_video = data.get('name_video')
    os.makedirs(f'media/{video_id}', exist_ok=True)
    os.makedirs(f'media/{video_id}/voice', exist_ok=True)
    os.makedirs(f'media/{video_id}/video', exist_ok=True)
    os.makedirs(f'media/{video_id}/video_backrought', exist_ok=True)
    os.makedirs(f'media/{video_id}/image', exist_ok=True)
    
    text_entries = json.loads(text)
    total_entries = len(text_entries)
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(process_entry, data, index, item, total_entries, video_id, task_id, worker_id): index
            for index, item in enumerate(text_entries, start=1)
        }
        for future in as_completed(futures):
            index = futures[future]
            try:
                result = future.result()
                if result:
                    percentage =(index / total_entries) * 100
                    update_status_video(f"Đang Render: Đã xử lý thành công videos {percentage:.2f} ", video_id, task_id, worker_id)
                else:
                    update_status_video(f"Render Lỗi:Mục {index} xử lý thất bại. dừng render", video_id, task_id, worker_id)
                    return False
                    
            except Exception as e:
                update_status_video(f"Render Lỗi:Mục {index} xử lý thất bại. dừng render", video_id, task_id, worker_id)
                return False
            
            
    update_status_video(f"Đang Render: đang tạo file phụ đề ", video_id, task_id, worker_id)
    file_sub = f'media/{video_id}/subtitles.ass'
    file_video = f'media/{video_id}/input_files_video.txt'    
    
    color = data.get('font_color')
    color_backrought = data.get('color_backrought')
    color_border = data.get('stroke')
    font_text = data.get("font_name")
    font_size = data.get('font_size')
    stroke_text = data.get('stroke_size')

    ass_file = open(file_sub, 'w',encoding='utf-8')

    file_list_video = open(file_video, 'w',encoding='utf-8')

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
    ass_file.write(f"Style: Default,{font_text},{font_size},{color},{color_backrought},&H00000000,{color_border},0,0,0,0,100,100,0,0,1,{stroke_text},0,2,10,10,40,0\n\n")

    ass_file.write("[Events]\n")
    ass_file.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect,WrapStyle,Text\n")

    start_time = timedelta(0)
    for item in text_entries:
        path_audio  = f'media/{video_id}/voice/{item["id"]}.wav'
        file_list_video.write(f"file 'video/{item['id']}.mp4'\n")
        
        
        duration = get_audio_duration(path_audio)
        duration_milliseconds = duration * 1000
        end_time = start_time + timedelta(milliseconds=duration_milliseconds)
        
        ass_file.write(f"Dialogue: 0,{format_timedelta_ass(start_time)},{format_timedelta_ass(end_time)},Default,,0,0,0,,2,{get_text_lines(data,item['text'])}\n")
        start_time = end_time
    
    ass_file.close()
    file_list_video.close()
    update_status_video(f"Đang Render: đã tạo thành công file phụ đề", video_id, task_id, worker_id)
    
    total_duration = end_time.total_seconds()
    
    ffmpeg_command = [
        'ffmpeg',
        '-f', 'concat',
        '-safe', '0',
        '-i', file_video,
        '-vf', f"subtitles={file_sub}",
        '-c:v', 'libx264',
        '-c:a', 'copy',  # Giữ nguyên âm thanh từ tệp video
        '-map', '0:v',   # Giữ video từ đầu vào
        '-map', '0:a',   # Giữ âm thanh từ đầu vào
        '-y',
        f"media/{video_id}/cache_video.mp4"
    ]
    
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
                update_status_video(f"Đang Render: xuất video hoàn thành {percentage:.2f}%", video_id, task_id, worker_id)
        process.wait()
        
    # Kiểm tra lỗi từ FFmpeg
    if process.returncode != 0:
        print(f"FFmpeg error:\n{process.stderr.read()}")
    else:
        update_status_video(f"Đang Render: xuất video hoàn thành công", video_id, task_id, worker_id)
        
    if data.get('channel_music_active'):
        update_status_video(f"Đang Render: đang chèn nhạc nền vào video ", video_id, task_id, worker_id)
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
            update_status_video(f"Đang Render: Đã xuất video và chèn nhạc nền thành công , chuẩn bị upload lên sever", video_id, task_id, worker_id)

    else:
        shutil.move(f"media/{video_id}/cache_video.mp4", f'media/{video_id}/{name_video}.mp4')
        update_status_video(f"Đang Render: Đã xuất video hoàn thành chuẩn bị upload lên sever", video_id, task_id, worker_id)
    return True
        

    
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


def update_status_video(status_video,video_id,task_id,worker_id):
    data = {
        'secret_key': SECRET_KEY,
        'action': 'update_status',
        'video_id': video_id,
        'status': status_video,
        'task_id': task_id,
        'worker_id': worker_id,
    }
    url = f'{SERVER}/api/'
    response = requests.post(url, json=data)
    if response.status_code == 200:
        print("Trạng thái video đã được cập nhật thành công.")
    else:
        print(f"Lỗi cập nhật trạng thái video: {response.status_code}")