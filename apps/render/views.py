from django.http.request import HttpRequest as HttpRequest
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse

from apps.home.models import Folder, Font_Text, syle_voice, Voice_language, ProfileChannel
from .models import VideoRender, DataTextVideo, video_url,Count_Use_data,Api_Key_Azure,Api_Voice_ttsmaker

from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from pytube import YouTube
import json ,re ,random ,string
from datetime import datetime, timedelta
from django.core.files.storage import default_storage
from storages.backends.sftpstorage import SFTPStorage

from .forms import VideoForm
from urllib.parse import urlparse, unquote
from django.core.cache import cache
from PIL import Image
from io import BytesIO
from apps.login.models import CustomUser
import calendar
import os
from django.http import FileResponse
from django.conf import settings

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
import time

from apps.render.task import render_video
from celery.result import AsyncResult

from .serializers import RenderSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from apps.home.models import Voice_language, syle_voice,Folder,ProfileChannel

from apps.home.serializers import ProfileSerializer

from itertools import chain
from django.db.models import Q



class ProfileChannelViewSet(viewsets.ModelViewSet):
    queryset = ProfileChannel.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['POST'])
    def add_videos(self, request, pk=None):
        profile = ProfileChannel.objects.select_related('folder_name').get(id=pk)
        folder_id = profile.folder_name.id
        upload_time = request.data.get('upload_time')
        upload_date = request.data.get('upload_date')
        characters = int(request.data.get('characters', 0))

        all_data = VideoRender.objects.filter(profile_id=profile)

        all = all_data.values_list('url_video_youtube', flat=True)
        
        all_urls = DataTextVideo.objects.filter(folder_id=folder_id).exclude(url_video__in=all)

        List_video = DataTextVideo.objects.filter(folder_id=folder_id).exclude(url_video__in=all_urls)

        if sum([video.count_text for video in List_video]) < characters:
            return JsonResponse({'error': 'Không Đủ Ký Tự Để Thêm Video Theo Yêu Cầu'}, status=status.HTTP_404_NOT_FOUND)
        total_count_text = 0
        count = 1
        text_video = ""
        video_url = []

        while total_count_text < characters and List_video.exists():
            # Chọn ngẫu nhiên một video từ List_video
            video = List_video.order_by('?').first()    
            # Cập nhật tổng count_text
            total_count_text += video.count_text
            
            # Loại bỏ video đã chọn khỏi List_video
            List_video = List_video.exclude(id=video.id)

            text_video += f"\n------------------------------- Video {count}  ------------------------------------------\n\n"
            text_video += f'Url video {video.url_video} \n\n'
            text_video += f'-----------------------------------------------------------------------------------------\n\n'
            text_video += video.text_video
            print(text_video)
            print("xxxxx")
            count += 1
            video_url.append(video)
        self.create_video_render(folder_id, profile, text_video, upload_time, upload_date, video_url)

        return JsonResponse({'success': True, 'message': 'Thêm video thành công!', 'text_video': text_video}, status=status.HTTP_201_CREATED)

    def cread_video_render(self, folder_id, profile, text_video, url_id, upload_time, upload_date):
        try:
            VideoRender.objects.create(
                folder_id=Folder.objects.get(id=folder_id),
                profile_id=ProfileChannel.objects.get(id=profile.id),
                name_video=''.join(random.choices(string.ascii_letters + string.digits, k=7)),
                text_content=text_video,
                title='Đang chờ cập nhật',
                description=profile.channel_description,
                keywords=profile.channel_keywords,
                time_upload=upload_time,
                date_upload=upload_date,
                status_video="Render",
                is_render_start=False,
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
                voice=profile.channel_voice,
                voice_style=profile.channel_voice_style,
                voice_speed=profile.channel_voice_speed,
                voice_pitch=profile.channel_voice_pitch,
                voice_volume=profile.channel_voice_volume,
            )
            
            # Thêm các video vào trường ManyToManyField sau khi tạo đối tượng VideoRender
            video_render.url_text_video.add(*video_url)
        
        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VideoRenderViewSet(viewsets.ModelViewSet):
    queryset = VideoRender.objects.all()
    serializer_class = RenderSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        profile_id = self.request.query_params.get('profile_id', None)
        
        if profile_id:
            return VideoRender.objects.filter(profile_id=profile_id)        
        elif profile_id == '':
            return VideoRender.objects.none()
        return VideoRender.objects.all()
    
    @action(detail=True, methods=['POST'])
    def update_video_render(self, request, pk=None):
        input_data = {
            'title': request.data.get('title',''),
            'description': request.data.get('description',''),
            'keywords': request.data.get('keywords',''),
            'date_upload': request.data.get('date_upload',''),
            'time_upload': request.data.get('time_upload',''),
            'content': request.data.get('text_content',''),
            'content_2': request.data.get('text_content_2',''),
            'video_image': request.data.get('video_image',''),
            'file-thumnail': request.data.get('file-thumnail',None),
            'file-audio': request.data.get('file-audio',None),
            'file-srt': request.data.get('file-srt',None)
        }
        date_upload = input_data['date_upload']
        try:
            video = VideoRender.objects.get(id=pk)
        except VideoRender.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Video không tồn tại!'}, status=status.HTTP_404_NOT_FOUND)

        if date_upload:
            date_upload_datetime = datetime.strptime(date_upload, '%Y-%m-%d')
            date_formatted = date_upload_datetime.strftime('%Y-%m-%d')
        else:
            date_formatted = None

        return self.update_video_info(request, video, input_data, date_formatted)

    def handle_thumbnail(self, video, thumnail):
        if video.url_thumbnail:
            image = video.url_thumbnail
            file_name = self.get_filename_from_url(image)
            default_storage.delete(f"data/{video.id}/image/{file_name}")
            print("xong thumnail")
        filename = thumnail.name.strip().replace(" ", "_")
        file_name = default_storage.save(f"data/{video.id}/thumnail/{filename}", thumnail)
        file_url = default_storage.url(file_name)
        return file_url
    
    def handle_audio(self, video, audio):
        if video.url_audio:
            file = video.url_audio
            file_name = self.get_filename_from_url(file)
            default_storage.delete(f"data/{video.id}/audio/{file_name}")
            print("xong audio")
        filename = audio.name.strip().replace(" ", "_")
        file_name = default_storage.save(f"data/{video.id}/audio/{filename}", audio)
        file_url = default_storage.url(file_name)
        return file_url
    
    def handle_subtitle(self, video, subtitle):
        if video.url_subtitle:
            file = video.url_subtitle
            file_name = self.get_filename_from_url(file)
            default_storage.delete(f"data/{video.id}/subtitle/{file_name}")
            print("xong subtitle")

        filename = subtitle.name.strip().replace(" ", "_")
        file_name = default_storage.save(f"data/{video.id}/subtitle/{filename}", subtitle)
        file_url = default_storage.url(file_name)
        return file_url

    def update_video_info(self, request, video, input_data, date_formatted):
        is_edit_title = Count_Use_data.objects.filter(videoRender_id=video, creade_video=False, edit_title=True, edit_thumnail=False).first()
        is_edit_thumnail = Count_Use_data.objects.filter(videoRender_id=video, creade_video=False, edit_title=False, edit_thumnail=True).first()

        # Kiểm tra điều kiện cho tiêu đề
        if input_data.get('title') and input_data['title'] != video.title:
            if is_edit_title and (not request.user.is_superuser and is_edit_title.use != request.user):
                return JsonResponse({'success': False, 'message': f'Tiêu đề đang được chỉnh sửa bởi người khác ({is_edit_title.use.username})!'}, status=status.HTTP_400_BAD_REQUEST)

        # Kiểm tra điều kiện cho thumbnail
        if input_data.get('file-thumnail'):
            if is_edit_thumnail and (not request.user.is_superuser and is_edit_thumnail.use != request.user):
                return JsonResponse({'success': False, 'message': f'Thumbnail đang được chỉnh sửa bởi người khác ({is_edit_thumnail.use.username})!'}, status=status.HTTP_400_BAD_REQUEST)

        # Nếu tất cả điều kiện thỏa mãn, tiến hành cập nhật và lưu
        try:
            if input_data.get('title') and input_data['title'] != video.title:
                if is_edit_title:
                    is_edit_title.title = input_data['title']
                else:
                    Count_Use_data.objects.create(videoRender_id=video, use=request.user, edit_title=True, title=input_data['title'])
                video.title = input_data['title']

            if input_data.get('description'):
                video.description = input_data['description']
            if input_data.get('keywords'):
                video.keywords = input_data['keywords']
            if input_data.get('time_upload'):
                video.time_upload = input_data['time_upload']
            if date_formatted:
                video.date_upload = date_formatted
            if input_data.get('content'):
                video.text_content = input_data['content']
            if input_data.get('content_2'):
                video.text_content_2 = input_data['content_2']
            if input_data.get('video_image'):
                video.video_image = input_data['video_image']

            if input_data.get('file-thumnail'):
                video.url_thumbnail = self.handle_thumbnail(video, input_data['file-thumnail'])
                if not is_edit_thumnail:
                    Count_Use_data.objects.create(videoRender_id=video, use=request.user, edit_thumnail=True, url_thumnail=video.url_thumbnail)

            if (input_data.get('file-audio') or input_data.get('file-srt')):
                if not video.url_audio or not video.url_subtitle:
                    return JsonResponse({'success': False, 'message': 'Vui lòng điền đầy đủ file audio và phụ đề'}, status=status.HTTP_400_BAD_REQUEST)
            
            if input_data.get('file-audio'):
                video.url_audio = self.handle_audio(video, input_data['file-audio'])
            if input_data.get('file-srt'):
                video.url_subtitle = self.handle_subtitle(video, input_data['file-srt'])
            # Lưu tất cả các thay đổi sau khi cập nhật
            video.save()
            if is_edit_title:
                is_edit_title.save()
            if is_edit_thumnail:
                is_edit_thumnail.save()

        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Đã xảy ra lỗi khi cập nhật video: ' + str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return JsonResponse({'success': True, 'message': 'Cập nhật video thành công!'}, status=status.HTTP_200_OK)
    
    def get_filename_from_url(self, url):
        parsed_url = urlparse(url)
        path = unquote(parsed_url.path)
        filename = path.split('/')[-1]
        return filename
    
    @action(detail=False, methods=['POST'])
    def status(self, request):
        list_video = request.data.get('list_video')
        number_list = list(map(int, list_video.split(',')))
        data = VideoRender.objects.filter(id__in=number_list)
        # Chuyển QuerySet thành danh sách các từ điển
        data_list = list(data.values())

        current_date = timezone.now().date()
        # Lọc theo ngày hiện tại
        if request.user.is_superuser:
            cread_video = Count_Use_data.objects.filter(creade_video=True, timenow=current_date).count()
            edit_title = Count_Use_data.objects.filter(edit_title=True, timenow=current_date).count()
            edit_thumnail = Count_Use_data.objects.filter(edit_thumnail=True, timenow=current_date).count()
            text = f'<span class="text-primary">{current_date}</span> ----Video: <span class="text-danger">{cread_video}</span> ---- Tittel: <span class="text-danger">{edit_title}</span> ---- Thumnail: <span class="text-danger">{edit_thumnail}</span>'
            
        else:
            cread_video = Count_Use_data.objects.filter(use=request.user, creade_video=True, timenow=current_date).count()
            edit_title = Count_Use_data.objects.filter(use=request.user, edit_title=True, timenow=current_date).count()
            edit_thumnail = Count_Use_data.objects.filter(use=request.user, edit_thumnail=True, timenow=current_date).count()
            text = f'<span class="text-primary">{current_date}</span> ---- VIDEO: <span class="text-danger">{cread_video}</span> ---- Tiêu ĐỀ: <span class="text-danger">{edit_title}</span> ---- Thumnail: <span class="text-danger">{edit_thumnail}</span>'
        return JsonResponse({'success': True, 'data': data_list ,'text':text}, status=status.HTTP_200_OK)

class index(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    template_name = 'render/index.html'

    def get(self, request):
        # folder = Folder.objects.first()
        # profiles = ProfileChannel.objects.filter(folder_name=folder)
        # current_time = timezone.now().strftime('%Y-%m-%d')
        # form = {
        #     'folder': Folder.objects.all(),
        #     'profiles': profiles,
        #     'current_time': current_time
        # }

        content = True
        if request.user.is_superuser:
            folders = Folder.objects.filter(is_content=content)
        else:
            folders = Folder.objects.filter(use=request.user.id, is_content=content)

        folders_first = folders.first() if folders.exists() else None
        profiles = ProfileChannel.objects.filter(folder_name_id=folders_first.id) if folders_first else []
        current_time = timezone.now().strftime('%Y-%m-%d')
        form = {
            'folder': folders,
            'profiles': profiles,
            'current_time': current_time,
            'content': content
        }

        VideoRender.objects.all().update(font_color='#FFFFFF',font_color_troke='#000000',stroke_text=3)



        return render(request, self.template_name,form)
    

    def get_filename_from_url(self,url):
        parsed_url = urlparse(url)
        path = unquote(parsed_url.path)
        filename = path.split('/')[-1]
        return filename
    
    
    def post(self, request):
        action = request.POST.get('action')
        if action == 'add-image-video':
            channel_name = request.POST.get('id-video-render')
            profile = VideoRender.objects.get(id=channel_name)
            image = request.FILES.get('file')
            if image:
                filename = image.name.strip().replace(" ", "_")
                file_image = default_storage.save(f"data/{profile.id}/image/{filename}", image)
                file_url = default_storage.url(file_image)
                return JsonResponse({'success': True, 'url': file_url})
            
        elif action == 'delete-image-video':
            channel_name = request.POST.get('id-video-render')
            image = request.POST.get('image_url')
            file_name = self.get_filename_from_url(image)
            default_storage.delete(f"data/{channel_name}/image/{file_name}")
            return JsonResponse({'success': True, 'message': 'Xóa ảnh thành công!'})

        elif action == "render-video":
            channel_name = request.POST.get('id-video-render')
            video = VideoRender.objects.get(id=channel_name)
            data = self.get_infor_render(video.id)
            try:
                if "render" in video.status_video:
                    task = render_video.apply_async(args=[data])
                    video.task_id = task.id
                    video.status_video = " Đang chờ render : Đợi đến lượt"
                    video.save()
                    return JsonResponse({'success': True, 'message': 'Video đang chờ render!'})
                
                elif "Render Lỗi" in video.status_video:
                    task = render_video.apply_async(args=[data])
                    video.task_id = task.id
                    video.status_video = "Đang chờ render : Render Lại"
                    video.save()
                    return JsonResponse({'success': True, 'message': 'Video đang chờ render!'})
                
                elif "Đang Chờ Render" in video.status_video or "Đang Render" in video.status_video:
                    result = AsyncResult(video.task_id)
                    result.revoke(terminate=True)
                    video.task_id = ''
                    video.status_video = "Render Lỗi : Dừng Render"
                    video.save()
                    print("xxxxxxx")
                    return JsonResponse({'success': True, 'message': 'Video đang chờ render!'})
                
                elif "Render Thành Công" in video.status_video or "Đang Upload Lên VPS" in video.status_video or "Upload VPS Thành Công" in video.status_video or "Upload VPS Thất Bại" in video.status_video:
                    task = render_video.apply_async(args=[data])
                    video.task_id = task.id
                    video.status_video = "Đang chờ render"
                    folder_path = f"data/{video.id}"
                    file = self.get_filename_from_url(video.url_video)
                    default_storage.delete(f"{folder_path}/{file}")
                    video.url_video = ''
                    video.save()
                    return JsonResponse({'success': True, 'message': 'Video đang được render!'})
                else:
                    return JsonResponse({'success': False, 'message': 'Trạng thái video không hợp lệ!'})
            except Exception as e:
                return JsonResponse({'success': False, 'message': f'Lỗi xảy ra: {str(e)}'})
    
    def handle_thumbnail(self,video, thumnail, video_id):
        if video.url_thumbnail:
            image = video.url_thumbnail
            file_name = self.get_filename_from_url(image)
            default_storage.delete(f"data/{video_id}/image/{file_name}")
        filename = thumnail.name.strip().replace(" ", "_")
        file_name = default_storage.save(f"data/{video_id}/thumnail/{filename}", thumnail)
        file_url = default_storage.url(file_name)
        video.url_thumbnail = file_url
        return file_url

    def update_video_info(self,video, input_data, date_formatted, json_text, thumnail, video_id):
        video.title = input_data['title']
        video.description = input_data['description']
        video.keywords = input_data['keyword']
        video.time_upload = input_data['time_upload']
        video.date_upload = date_formatted
        video.text_content = input_data['content']
        video.video_image = input_data['video_image']
        video.text_content_2 = json_text
        if thumnail:
            video.url_thumbnail = self.handle_thumbnail(video, thumnail, video_id)
        video.save()

    def get_infor_render(self,id_video):
        video = VideoRender.objects.get(id=id_video)
        language = Voice_language.objects.get(id=video.voice)
        voice = syle_voice.objects.get(id=video.voice_style)
        data  = {
            'video_id': video.id,
            'name_video': video.name_video,
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
            'language': language.name,
            'style': voice.id_style,
            'name_langue': voice.name_voice,
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

class VideoRenderList(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    template_name = 'render/count_data_use.html'
    def get(self, request):
        current_date = timezone.now().date()
        data = []
        date = current_date.strftime("%Y-%m-%d")
        all_users = CustomUser.objects.all()
        for user in all_users:
            cread_video = Count_Use_data.objects.filter(use=user, creade_video=True, timenow=current_date).count()
            edit_title = Count_Use_data.objects.filter(use=user, edit_title=True, timenow=current_date).count()
            edit_thumnail = Count_Use_data.objects.filter(use=user, edit_thumnail=True, timenow=current_date).count()
            data.append({
                'user': user,
                'cread_video': cread_video,
                'edit_title': edit_title,
                'edit_thumnail': edit_thumnail
            })

        directory_path = 'test 001'
        default_storage.mkdir(directory_path)
        
        return render(request, self.template_name, {'data': data, 'current_date_old': date, 'current_date_new': date})
    

    

    def post(self, request):
        action = request.POST.get('action')
        if action == 'Seach':
            date_upload_old = request.POST.get('date_upload_old')
            date_upload_new = request.POST.get('date_upload_new')

            # Chuyển đổi chuỗi ngày tháng thành đối tượng datetime
            date_upload_old = timezone.datetime.strptime(date_upload_old, '%Y-%m-%d').date()
            date_upload_new = timezone.datetime.strptime(date_upload_new, '%Y-%m-%d').date()

            date_old = date_upload_old.strftime("%Y-%m-%d")
            date_new = date_upload_new.strftime("%Y-%m-%d")
            data = []
            all_users = CustomUser.objects.all()

            for user in all_users:
                cread_video = Count_Use_data.objects.filter(use=user, creade_video=True, timenow__range=[date_upload_old, date_upload_new]).count()
                edit_title = Count_Use_data.objects.filter(use=user, edit_title=True, timenow__range=[date_upload_old, date_upload_new]).count()
                edit_thumnail = Count_Use_data.objects.filter(use=user, edit_thumnail=True, timenow__range=[date_upload_old, date_upload_new]).count()
                data.append({
                    'user': user,
                    'cread_video': cread_video,
                    'edit_title': edit_title,
                    'edit_thumnail': edit_thumnail
                })

            return render(request, self.template_name, {'data': data, 'current_date_old': date_old, 'current_date_new': date_new})
        
        if action == 'Date-Yesterday':
            current_date = timezone.now().date() - timedelta(days=1)
            date = current_date.strftime("%Y-%m-%d")
            data = []
            all_users = CustomUser.objects.all()
            for user in all_users:
                cread_video = Count_Use_data.objects.filter(use=user, creade_video=True, timenow=current_date).count()
                edit_title = Count_Use_data.objects.filter(use=user, edit_title=True, timenow=current_date).count()
                edit_thumnail = Count_Use_data.objects.filter(use=user, edit_thumnail=True, timenow=current_date).count()
                data.append({
                    'user': user,
                    'cread_video': cread_video,
                    'edit_title': edit_title,
                    'edit_thumnail': edit_thumnail
                })
            return render(request, self.template_name, {'data': data, 'current_date_old': date, 'current_date_new': date})
        
        if action == 'Date-Today':
            current_date = timezone.now().date()
            date = current_date.strftime("%Y-%m-%d")
            data = []
            all_users = CustomUser.objects.all()
            for user in all_users:
                cread_video = Count_Use_data.objects.filter(use=user, creade_video=True, timenow=current_date).count()
                edit_title = Count_Use_data.objects.filter(use=user, edit_title=True, timenow=current_date).count()
                edit_thumnail = Count_Use_data.objects.filter(use=user, edit_thumnail=True, timenow=current_date).count()
                data.append({
                    'user': user,
                    'cread_video': cread_video,
                    'edit_title': edit_title,
                    'edit_thumnail': edit_thumnail
                })
            return render(request, self.template_name, {'data': data, 'current_date_old': date, 'current_date_new': date})
        
        if action == "Date-Month":
            current_date = timezone.now().date()
            first_day = current_date.replace(day=1)
            last_day = current_date.replace(day=calendar.monthrange(current_date.year, current_date.month)[1])
            date_old = first_day.strftime("%Y-%m-%d")
            date_new = last_day.strftime("%Y-%m-%d")
            data = []
            all_users = CustomUser.objects.all()

            for user in all_users:
                cread_video = Count_Use_data.objects.filter(use=user, creade_video=True, timenow__range=[first_day, last_day]).count()
                edit_title = Count_Use_data.objects.filter(use=user, edit_title=True, timenow__range=[first_day, last_day]).count()
                edit_thumnail = Count_Use_data.objects.filter(use=user, edit_thumnail=True, timenow__range=[first_day, last_day]).count()
                data.append({
                    'user': user,
                    'cread_video': cread_video,
                    'edit_title': edit_title,
                    'edit_thumnail': edit_thumnail
                })

            return render(request, self.template_name, {
                'data': data, 
                'current_date_old': date_old, 
                'current_date_new': date_new
            })

        elif action == 'show-thumnail':
            id = request.POST.get('id')
            page = request.POST.get('page')
            date_upload_old = request.POST.get('current_date_old')
            date_upload_new = request.POST.get('current_date_new')
            user = CustomUser.objects.get(id=id)
            data = Count_Use_data.objects.filter(use=user, edit_thumnail=True, timenow__range=[date_upload_old, date_upload_new])
            paginator = Paginator(data,9)
            page_obj = paginator.get_page(page)
            thumnail = render_to_string('render/show-image.html', {'page_obj': page_obj}, request)
            page_obj = render_to_string('render/thumnail_page_bar_template.html', {'page_obj': page_obj}, request)
            return JsonResponse({'success': True, 'thumnail_html': thumnail, 'page_bar_html': page_obj})
        

        elif action == 'show-title':
            id = request.POST.get('id')
            page = request.POST.get('page')
            date_upload_old = request.POST.get('current_date_old')
            date_upload_new = request.POST.get('current_date_new')

            # Chuyển đổi chuỗi ngày tháng thành đối tượng datetime
            date_upload_old = timezone.datetime.strptime(date_upload_old, '%Y-%m-%d').date()
            date_upload_new = timezone.datetime.strptime(date_upload_new, '%Y-%m-%d').date()

            user = CustomUser.objects.get(id=id)
            data = Count_Use_data.objects.filter(use=user, edit_title=True, timenow__range=[date_upload_old, date_upload_new])
            paginator = Paginator(data, 10)
            page_obj = paginator.get_page(page)

            # Sử dụng page_obj thay vì paginator khi gọi render_to_string
            title_html = render_to_string('render/show-title.html', {'page_obj': page_obj}, request)
            page_bar_html = render_to_string('render/title_page_bar_template.html', {'page_obj': page_obj}, request)

            return JsonResponse({'success': True, 'title_html': title_html, 'page_bar_html': page_bar_html})
        

def download_file(request):
    file_path = os.path.join(settings.BASE_DIR, 'AppUpload.rar')
    # Sử dụng with để đảm bảo file được đóng đúng cách
    response = FileResponse(open(file_path, 'rb'), as_attachment=True, filename='AppUpload.rar')
    return response
