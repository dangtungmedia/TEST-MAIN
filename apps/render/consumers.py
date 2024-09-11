from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import sync_to_async, async_to_sync
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from channels.layers import get_channel_layer
from django.utils import timezone
from .models import VideoRender, Count_Use_data,DataTextVideo,APIKeyGoogle
from .serializers import RenderSerializer
from apps.login.models import CustomUser
from django.core.files.storage import default_storage

from apps.render.task import render_video,render_video_reupload
from celery.result import AsyncResult
from urllib.parse import urlparse, unquote
from asgiref.sync import async_to_sync
from django.core.files.base import ContentFile
import base64,re
from random import randint
import random
import string,requests
import logging
from pytube import YouTube
import os


from apps.home.models import Voice_language, syle_voice
from apps.home.models import Voice_language, syle_voice,Folder,ProfileChannel



@receiver(post_save, sender=VideoRender)
def notify_video_change(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    data = RenderSerializer(instance).data
    async_to_sync(channel_layer.group_send)(
        "public",
        {
            'type': 'chat_message',
            'message': 'update_status',
            'data': data
        }
    )

@receiver(post_delete, sender=VideoRender)
def notify_video_delete(sender, instance, **kwargs):

    channel_layer = get_channel_layer()
    video_path = f"data/{instance.id}/"

    if default_storage.exists(video_path):
        try:
            # Liệt kê tất cả các tệp và thư mục con
            dirs, files = default_storage.listdir(video_path)
            
            # Đệ quy xóa các thư mục con
            for directory in dirs:
                subdir_path = os.path.join(video_path, directory)
                delete_recursive(subdir_path)  # Hàm xóa đệ quy (được định nghĩa bên dưới)

            # Xóa tất cả các tệp trong thư mục
            for file in files:
                file_path = os.path.join(video_path, file)
                default_storage.delete(file_path)
            
            # Sau khi xóa hết tệp và thư mục con, xóa thư mục hiện tại
            default_storage.delete(video_path)

        except Exception as e:
            print(f"Error deleting files for video {instance.id}: {e}")

    # Thông báo qua WebSocket
    async_to_sync(channel_layer.group_send)(
        "public",
        {
            'type': 'chat_message',
            'message': 'btn-delete',
            'data': {
                'id': instance.id
            }
        }
    )

def delete_recursive(path):
    """Hàm đệ quy để xóa các thư mục con."""
    if default_storage.exists(path):
        dirs, files = default_storage.listdir(path)
        
        # Đệ quy xóa các thư mục con trước
        for directory in dirs:
            delete_recursive(os.path.join(path, directory))

        # Xóa các tệp trong thư mục hiện tại
        for file in files:
            default_storage.delete(os.path.join(path, file))
        
        # Xóa thư mục sau khi các tệp và thư mục con đã bị xóa
        default_storage.delete(path)
    

@receiver(post_save, sender=Count_Use_data)
def notify_count_video(sender, instance, **kwargs):
    user = instance.use
    current_date = timezone.now().date()
    channel_layer = get_channel_layer()
    
    # Kiểm tra quyền của người dùng và lấy dữ liệu tương ứng
    if user.is_staff:
        group = "User-admin"
        data = get_admin_count_data(current_date)
    else:
        group = str(user.id)
        data = get_user_count_data(user, current_date)


    print(f"Sending data: {data}")
    # Gửi thông báo qua kênh WebSocket
    async_to_sync(channel_layer.group_send)(
        group,
        {
            'type': 'chat_message',
            'message': 'update_count',
            'data': data
        }
    )

def get_admin_count_data(current_date):
    cread_video = Count_Use_data.objects.filter(creade_video=True, timenow=current_date).count()
    edit_title = Count_Use_data.objects.filter(edit_title=True, timenow=current_date).count()
    edit_thumnail = Count_Use_data.objects.filter(edit_thumnail=True, timenow=current_date).count()
    return f'<span class="text-primary">{current_date}</span> ---- Video: <span class="text-danger">{cread_video}</span> ---- Title: <span class="text-danger">{edit_title}</span> ---- Thumbnail: <span class="text-danger">{edit_thumnail}</span>'

def get_user_count_data(user, current_date):
    cread_video = Count_Use_data.objects.filter(use=user, creade_video=True, timenow=current_date).count()
    edit_title = Count_Use_data.objects.filter(use=user, edit_title=True, timenow=current_date).count()
    edit_thumnail = Count_Use_data.objects.filter(use=user, edit_thumnail=True, timenow=current_date).count()
    return f'<span class="text-primary">{current_date}</span> ---- VIDEO: <span class="text-danger">{cread_video}</span> ---- Tiêu ĐỀ: <span class="text-danger">{edit_title}</span> ---- Thumbnail: <span class="text-danger">{edit_thumnail}</span>'

class RenderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = None
        await self.accept()
        await self.channel_layer.group_add("public", self.channel_name)

    async def disconnect(self, close_code):
        if self.user_id:
            await self.channel_layer.group_discard(self.user_id, self.channel_name)
        await self.channel_layer.group_discard("public", self.channel_name)
        await self.channel_layer.group_discard("User-admin", self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError as e:
            await self.send(text_data=json.dumps({'error': 'Invalid JSON', 'details': str(e)}))
            return

        current_date = timezone.now().date()
        print(f"Current date: {current_date}")

        try:
            message_type = data['type']
            print(f"Message type: {message_type}")
        except KeyError as e:
            print(f"KeyError: {e}")
            print(f"Received data without 'type': {data}")
            await self.send(text_data=json.dumps({'error': "Message does not contain 'type' key"}))
            return

        if message_type == 'identify':
            self.user_id = data['user_id']
            is_staff = await self.check_if_staff(self.user_id)
            if is_staff:
                username = await self.get_username(self.user_id)
                await self.send(text_data=json.dumps({'message': 'User is an admin.', 'username': username}))
                await self.channel_layer.group_add("User-admin", self.channel_name)
                count_data = await sync_to_async(get_admin_count_data)(current_date)
            else:
                await self.send(text_data=json.dumps({'message': 'User is not an admin.'}))
                await self.channel_layer.group_add(str(self.user_id), self.channel_name)
                count_data = await sync_to_async(get_user_count_data)(self.user_id, current_date)
            await self.send(text_data=json.dumps({'message': 'update_count', 'data': count_data}))

        elif message_type == 'btn-play-video':
            self.id_video = data['id_video']
            url = await self.get_video_play(self.id_video)
            await self.send(text_data=json.dumps({'message': 'btn-play-video', 'data': url}))

        elif message_type == 'btn-render':
            self.id_video = data['id_video']
            await self.render_video(self.id_video)

        elif message_type == 'edit-video':
            video_data = await self.get_infor_edit_video(data['id_video'])
            await self.send(text_data=json.dumps({'message': 'btn-edit', 'data': video_data}))

        elif message_type == 'btn-re-upload':
            await self.reuploadFile(data['id_video'])


        elif message_type == 'add-one-video':
            video_data = await self.add_one_video(data)
            await self.send(text_data=json.dumps({'message': 'add-one-video', 'data': video_data}))

        elif message_type == 'add-text-folder':
            data = await self.add_text_folder(data)
            await self.send(text_data=json.dumps({'message': 'add-text-folder', 'data': video_data}))


        elif message_type == 'btn-delete':
           await self.delete_video(data)

            

        elif message_type == 'get-text-video':
            text  = await self.get_text_video(data)
            await self.send(text_data=json.dumps({'message': 'get-text-video', 'data': text}))

        elif message_type == "render-all" :
            channel_name = data.get('channel_name', None)
            if channel_name:
                await self.render_all_videos(channel_name)

        elif message_type == "render-erron":
            channel_name = data.get('channel_name', None)
            if channel_name:
                await self.render_erron(channel_name)
    
        elif message_type == "upload-erron":
            channel_name = data.get('channel_name', None)
            if channel_name:
                await self.upload_erron(channel_name)

        elif message_type == "delete-all-success":
            channel_name = data.get('channel_name', None)
            if channel_name:
                await self.delete_all_reup(channel_name)

    async def chat_message(self, event):
        message = event['message']
        data = event.get('data', {})

        await self.send(text_data=json.dumps({
            'message': message,
            'data': data 
        }))

    async def render_status(self, event):
        await self.update_status(event['data'])
        



    @sync_to_async
    def check_if_staff(self, user_id):
        try:
            user = CustomUser.objects.get(pk=user_id)
            return user.is_staff
        except CustomUser.DoesNotExist:
            return False

    @sync_to_async
    def get_username(self, user_id):
        try:
            user = CustomUser.objects.get(pk=user_id)
            return user.username
        except CustomUser.DoesNotExist:
            return None
        
    @sync_to_async
    def delete_all_reup(self, channel_name):
        render_all_videos = VideoRender.objects.filter(profile_id=channel_name, status_video__icontains='Upload VPS Thành Công')
        for video in render_all_videos:
            video.delete()

    @sync_to_async
    def upload_erron(self, channel_name):
        render_all_videos = VideoRender.objects.filter(profile_id=channel_name, status_video__icontains='Upload VPS Thất Bại')
        for video in render_all_videos:
            data = self.get_data_video(video.id)
            if video.folder_id.is_content:
                task = render_video.apply_async(args=[data])
            else:
                task = render_video_reupload.apply_async(args=[data])
            video.task_id = task.id
            video.status_video = "Render Thành Công : Đang Chờ Upload lại lên Kênh"
            video.save()


    @sync_to_async
    def render_erron(self, channel_name):
        render_all_videos = VideoRender.objects.filter(profile_id=channel_name, status_video__icontains='Render Lỗi')
        for video in render_all_videos:
            data = self.get_data_video(video.id)
            if video.folder_id.is_content:
                task = render_video.apply_async(args=[data])
            else:
                task = render_video_reupload.apply_async(args=[data])
            video.task_id = task.id
            video.status_video = "Đang chờ render : Đợi đến lượt render lại"
            video.save()

    @sync_to_async
    def render_all_videos(self, channel_name):
        render_all_videos = VideoRender.objects.filter(profile_id=channel_name, status_video='render')
        for video in render_all_videos:
            data = self.get_data_video(video.id)
            if video.folder_id.is_content:
                    task = render_video.apply_async(args=[data])
            else:
                task = render_video_reupload.apply_async(args=[data])
            video.task_id = task.id
            video.status_video = "Đang chờ render : Đợi đến lượt render"
            video.save()



    @sync_to_async
    def render_video(self, id_video):
        video = VideoRender.objects.get(pk=id_video)
        data = self.get_data_video(video.id)
        if video.status_video == "render":
            try:
                if video.folder_id.is_content:
                    task = render_video.apply_async(args=[data])
                else:
                    task = render_video_reupload.apply_async(args=[data])
                video.task_id = task.id
                video.status_video = "Đang chờ render : Đợi đến lượt render"
                video.save()

            except Exception as e:
                video.status_video = "Render Lỗi : Dừng Render"
                video.save()

        elif "Đang chờ render" in video.status_video or "Đang Render" in video.status_video:
            try:
                result = AsyncResult(video.task_id)
                result.revoke(terminate=True)
                video.task_id = ''
                video.status_video = "Render Lỗi : Dừng Render"
                video.save()
            except Exception as e:
                video.status_video = "Render Lỗi : Dừng Render"
                video.save()
        
        elif "Render Lỗi" in video.status_video:
            try:
                if video.folder_id.is_content:
                    task = render_video.apply_async(args=[data])
                else:
                    task = render_video_reupload.apply_async(args=[data])
                video.task_id = task.id
                video.status_video = "Đang chờ render : Render Lại"
                video.save()

            except Exception as e:
                video.status_video = "Render Lỗi : Dừng Render"
                video.save()

        elif "Render Thành Công" in video.status_video or "Đang Upload Lên VPS" in video.status_video or "Upload VPS Thành Công" in video.status_video or "Upload VPS Thất Bại" in video.status_video:
            try:
                if video.folder_id.is_content:
                    task = render_video.apply_async(args=[data])
                else:
                    task = render_video_reupload.apply_async(args=[data])
                video.task_id = task.id
                video.status_video = "Đang chờ render : Render Lại"
                folder_path = f"data/{video.id}"
                file = self.get_filename_from_url(video.url_video)
                default_storage.delete(f"{folder_path}/{file}")
                video.url_video = ''
                video.save()
            except Exception as e:
                video.status_video = "Render Lỗi : Dừng Render"
                video.save()

    @sync_to_async
    def update_status(self, data):
        video = VideoRender.objects.get(id=data['video_id'])
        video.status_video = data['status']
        video.save()

    @sync_to_async
    def get_infor_edit_video(self, id_video):
        video = VideoRender.objects.get(id=id_video)
        return RenderSerializer(video).data

    @sync_to_async
    def add_one_video(self, data):
        try:
            profile = ProfileChannel.objects.get(id=data['profile_id'])
            user = CustomUser.objects.get(id=data['userId'])
            thumbnail_base64 = data['thumbnail']
            file_url = ''

            file_name = ''.join(random.choices(string.ascii_letters + string.digits, k=7)) + '.png'
            if thumbnail_base64:
                thumbnail_data = ContentFile(base64.b64decode(thumbnail_base64), name=file_name)
                thumbnail_path = default_storage.save(f"thumbnails/{thumbnail_data.name}", thumbnail_data)
                file_url = default_storage.url(thumbnail_path)
                
            video = VideoRender.objects.create(
                folder_id= profile.folder_name,
                profile_id= profile,
                name_video=''.join(random.choices(string.ascii_letters + string.digits, k=7)),

                title= data['title'],
                description= data['description'],
                keywords= data['keywords'],
                time_upload= data['time_upload'],
                date_upload= data['date_upload'],
            
                status_video = 'render',
                is_render_start = True,
                url_thumbnail = file_url,
                intro_active=profile.channel_intro_active,
                intro_url=profile.channel_intro_url,
                outro_active=profile.channel_outro_active,
                outro_url=profile.channel_outro_url,
                logo_active=profile.channel_logo_active,
                logo_url=profile.channel_logo_url,
                logo_position=profile.channel_logo_position,
                font_text=profile.channel_font_text,
                font_size=profile.channel_font_size,
                font_bold=profile.channel_font_bold,
                font_italic=profile.channel_font_italic,
                font_underline=profile.channel_font_underline,
                font_strikeout=profile.channel_font_strikeout,
                font_color=profile.channel_font_color,
                font_color_opacity=profile.channel_font_color_opacity,
                font_color_troke=profile.channel_font_color_troke,
                font_color_troke_opacity=profile.channel_font_color_troke_opacity,
                stroke_text=profile.channel_stroke_text,
                font_background=profile.channel_font_background,
                channel_font_background_opacity=profile.channel_font_background_opacity,
                channel_voice_style=profile.channel_voice_style,
            )
            if not user.is_staff:
                Count_Use_data.objects.create(use=user,videoRender_id=video, creade_video=True, timenow=timezone.now().date())
                Count_Use_data.objects.create(use=user, videoRender_id=video, edit_title=True, timenow=timezone.now().date())
                if file_url:
                    Count_Use_data.objects.create(use=user,videoRender_id=video, edit_thumnail=True, timenow=timezone.now().date())
            return RenderSerializer(video).data
        except ProfileChannel.DoesNotExist:
            return None

    @sync_to_async
    def add_text_folder(self, data):
        is_valid, url,channel_id,title = self.check_video_url(data['url'])
        if is_valid:
            is_url = video_url.objects.filter(url=url).exists()
            if is_url:
                return {'success': False, 'message': 'Video đã tồn tại không thể thêm tiếp !'}
            else:
                DataTextVideo.objects.create(
                    folder_id=Folder.objects.get(id=data['folder']),
                    url_video=url,
                    count_text=len(data['text']),
                    id_channel=channel_id,
                    title=title,
                    text_video= data['text']
                )
                return {'success': True, 'message': "Thêm url thành công rồi nhé !"}
        else:
            return {'success': False, 'message': f"Lỗi không thể đọc được url {url}"}

    @sync_to_async
    def delete_video(self, data):
        try:
            user = CustomUser.objects.get(id=data['userId'])
            if user.is_deleted or user.is_staff:
                video = VideoRender.objects.get(id=data['id_video'])
                video.delete()
                return {'success': True,"id_video": data['id_video'], "message": "Xóa Video Thành Công"}
            else:
                return {'success': False,"id_video": data['id_video'], "message": "Bạn Không Có Quyền Xóa Liên Hệ Admin"}
        except VideoRender.DoesNotExist:
            return {'success': False,"id_video":None,"message": "Video không tồn tại"}

    @sync_to_async
    def get_video_play(self,id_video):
        video = VideoRender.objects.get(id=id_video)
        return video.url_video
    
    @sync_to_async
    def get_text_video(self,data):
        image_data = data['image']
        image_data = image_data.replace('data:image/png;base64,', '')
        image_bytes = base64.b64decode(image_data)

        # Tạo tên file duy nhất
        KEY_API_GOOGLE = APIKeyGoogle.objects.first().key

        url = f'https://vision.googleapis.com/v1/images:annotate?key={KEY_API_GOOGLE}'

        request_data = {
            "requests": [
                {
                    "image": {
                        "content": base64.b64encode(image_bytes).decode('utf-8')
                    },
                    "features": [
                        {
                            "type": "TEXT_DETECTION"
                        }
                    ]
                }
            ]
        }

        response = requests.post(url, json=request_data)

        if response.status_code == 200:
            try:
                response_text = response.json()['responses'][0]['fullTextAnnotation']['text']
                return response_text
            except KeyError:
                response_text = 'Không nhận diện được văn bản'
            return response_text
        else:
            print(f'Error: {response.status_code}')
            print(response.json())
       
    @sync_to_async
    def reuploadFile(self,id_video):
        video = VideoRender.objects.get(id=id_video)
        if "Upload VPS Thất Bại" in video.status_video or "Upload VPS Thành Công" in video.status_video or "Đang Upload Lên VPS" in video.status_video:
            video.status_video = "Render Thành Công : Đang Chờ Upload lên Kênh"
            video.save()

    def check_video_url(self,url):
        match = re.match(r'https?://www\.youtube\.com/watch\?v=.+', url)
        if not match:
            return False, "Vui Lòng Nhập Đúng Url Video", None, None
        try:        
            yt = YouTube(url)

            channel_id = yt.channel_id

            url = yt.watch_url

            title = yt.title
            return True, url, channel_id, title
        except:
            return False, "Video Không Tồn Tại ", None, None

    def get_filename_from_url(self,url):
        parsed_url = urlparse(url)
        path = unquote(parsed_url.path)
        filename = path.split('/')[-1]
        return filename
      
    def get_data_video(self, id_video):
        try:
            data = self.get_infor_render(id_video)
            return data
        except VideoRender.DoesNotExist:
            return None
    
    def get_infor_render(self,id_video):
        video = VideoRender.objects.get(id=id_video)
        data  = {
            "is_content": video.folder_id.is_content,
            'url_reupload': video.url_reupload,
            "url_video_youtube": video.url_video_youtube,
            'video_id': video.id,
            'name_video': video.name_video,
            'text': video.text_content,
            'text_content': video.text_content_2,
            'images': video.video_image,
            'font_name': video.font_text.font_name,
            'font_size': video.font_size,
            'font_bold': video.font_bold,
            'font_italic': video.font_italic,
            'font_underline': video.font_underline,
            'font_strikeout': video.font_strikeout,
            'font_color': self.convert_color_to_ass(video.font_color,video.font_color_opacity),
            'color_backrought': self.convert_color_to_ass(video.font_background,video.channel_font_background_opacity),
            'stroke': self.convert_color_to_ass(video.font_color_troke,video.font_color_troke_opacity),
            'stroke_size': video.stroke_text,
            'language': video.channel_voice_style.voice_language.name,
            'style': video.channel_voice_style.style_name,
            'voice_id': video.channel_voice_style.id_style,
            'name_langue': video.channel_voice_style.name_voice,
            'url_audio': video.url_audio,
            'file-srt': video.url_subtitle,
            }
        return data

    def convert_color_to_ass(self,color_hex, opacity):
        # Chuyển đổi mã màu HEX sang RGB
        r = int(color_hex[1:3], 16)
        g = int(color_hex[3:5], 16)
        b = int(color_hex[5:7], 16)
        
        # Tính giá trị Alpha từ độ trong suốt
        alpha = round(255 * (1 - opacity / 100))
        
        # Định dạng lại thành mã màu ASS
        ass_color = f"&H{alpha:02X}{b:02X}{g:02X}{r:02X}&"
        
        return ass_color


   
