from django.test import TestCase
# Create your tests here.
response_1 = requests.get('http://127.0.0.1:50021/speakers')
    list_voice = response_1.json()
    data = Voice_language.objects.all()
    for iteam in data:
        if iteam.name == 'Japanese':
            for voice in list_voice:
                for style in voice['styles']:
                    syle_voice.objects.create(id_style=style['id'],name_voice=voice['name'],style_name=f"{voice['name']}-{style['name']}",voice_language=iteam)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.files.storage import default_storage
from django.http import FileResponse
from django.core.cache import cache
import os
import shutil
import tempfile
import requests
from apps.render.views import get_video_render_data_from_cache

from apps.home.models import Voice_language, syle_voice,ProfileChannel
from apps.render.models import VideoRender
import json

class ApiApp(APIView):
    permission_classes = [AllowAny]  # Cho phép mọi request không cần đăng nhập
    # def get(self, request):
    #     return Response({"message": "Hello, world!"})
    
    # def post(self, request):
    #     action = request.data.get('action')
    #     if action == 'get_video_render':
    #         cache_render = get_video_render_data_from_cache()
    #         video = ''
    #         for iteam in cache_render:
    #             if iteam['id'] == 9:
    #                 video = iteam
    #                 break
    #             if iteam['status_video'] == 'Đang chờ render video!' and iteam['is_render_start'] == True:
    #                 video = iteam
    #                 break
    #         if not video:
    #             for iteam in cache_render:
    #                 if iteam['status_video'] == 'Đang chờ render video!':
    #                     video = iteam
    #                     break 

    #         if not video:
    #             return Response({"error": "Video not found"}, status=404)
    #         data = self.get_json_video_render(video)  
    #         return Response(data)
        
        
    #     elif action == 'download_image':
    #         id_video = request.data.get('id')
    #         file_name = request.data.get('filename')
    #         if not file_name:
    #             return Response({"error": "file_image is required"}, status=400)

    #         directory_path = f"data/{id_video}/image/{file_name}"
            
    #         # Kiểm tra xem tệp có tồn tại hay không
    #         if not default_storage.exists(directory_path):
    #             return Response({"error": "File not found"}, status=404)
    #         # Trả về tệp
    #         file = default_storage.open(directory_path, 'rb')
    #         response = FileResponse(file)
    #         response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    #         return response
        
    #     elif action == 'download_voice_japanese':
    #         text = request.data.get('text_voice')
    #         id_voice = request.data.get('id_voice')
    #         if not text:
    #             return Response({"error": "text_voice is required"}, status=400)

    #         # Bước 2: Gửi yêu cầu POST tới API để tạo JSON query
    #         url_query = f"http://voicevox_engine:50021/audio_query?speaker={id_voice}"
    #         response_query = requests.post(url_query, params={'text': text})
    #         query_json = response_query.json()

    #         # Bước 3: Thay đổi giá trị speedScale trong tệp JSON
    #         query_json["speedScale"] = 1

    #         # Bước 4: Gửi yêu cầu POST để tạo tệp âm thanh với tốc độ đã thay đổi
    #         url_synthesis = f"http://voicevox_engine:50021/synthesis?speaker={id_voice}"
    #         headers = {"Content-Type": "application/json"}
    #         response_synthesis = requests.post(url_synthesis, headers=headers, json=query_json)

    #         # Lưu tệp âm thanh kết quả vào một tệp tạm thời
    #         with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
    #             temp_audio_file.write(response_synthesis.content)
    #             temp_audio_path = temp_audio_file.name

    #         # Trả về tệp âm thanh kết quả
    #         response = FileResponse(open(temp_audio_path, 'rb'), content_type='audio/wav')
    #         response['Content-Disposition'] = 'attachment; filename="audio_fast.wav"'
            
    #         # Đóng và xóa tệp tạm thời sau khi trả về
    #         os.remove(temp_audio_path)
    #         return response
    
    # def get_json_video_render(self, video):
    #     voice = syle_voice.objects.get(id=video['voice_style'])
    #     # Chuyển đổi nội dung văn bản từ video thành JSON
    #     json_data = json.loads(video['text_content_2'])
    #     data = {
    #             'id': video['id'],
    #             'text': json_data,
    #             'font_text': video['font_text'],
    #             'font_size': video['font_size'],
    #             'font_bold': video['font_bold'],
    #             'font_italic': video['font_italic'],
    #             'font_underline': video['font_underline'],
    #             'font_strikeout': video['font_strikeout'],
    #             'stroke_text_size': video['stroke_text'],
    #             'font_color': self.convert_color_to_ass(video['font_color'], video['font_color_opacity']),
    #             'stroke_color': self.convert_color_to_ass(video['font_color_troke'], video['font_color_troke_opacity']),
    #             'bg_color': self.convert_color_to_ass(video['font_background'], video['channel_font_background_opacity']),
    #             'voice': voice.voice_language.name,
    #             'voice_style_id': voice.id_style,
    #             'voice_style_name_voice': voice.name_voice,
    #             'voice_speed': video['voice_speed'],
    #             'voice_pitch': video['voice_pitch'],
    #             'voice_volume': video['voice_volume'],
    #         }
    #     return data
    
    # def convert_color_to_ass(self,color_hex, opacity):
        # Chuyển đổi mã màu HEX sang RGB
        r = int(color_hex[1:3], 16)
        g = int(color_hex[3:5], 16)
        b = int(color_hex[5:7], 16)
        
        # Tính giá trị Alpha từ độ trong suốt
        alpha = round(255 * (1 - opacity / 100))
        
        # Định dạng lại thành mã màu ASS
        ass_color = f"&H{alpha:02X}{b:02X}{g:02X}{r:02X}&"
        
        return ass_color