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
from .forms import VideoForm
from urllib.parse import urlparse, unquote
from django.core.cache import cache
from PIL import Image
from io import BytesIO
from apps.login.models import CustomUser
import calendar
import os

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

from apps.render.cace_database import get_video_render_data_from_cache, update_video_render_data_from_cache, get_Data_Text_Video_data_from_cache, get_count_use_data_from_cache
    
class VideoRenderViewSet(viewsets.ModelViewSet):
    serializer_class = RenderSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        profile_id = self.request.query_params.get('profile_id', None)
        if profile_id:
            return VideoRender.objects.filter(profile_id=profile_id)
        
        # Nếu không có profile_id nhưng vẫn cần lấy đối tượng cụ thể theo ID
        if self.action == 'retrieve':
            return VideoRender.objects.all()
        return VideoRender.objects.none()

class index(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    template_name = 'render/index.html'

    def get(self, request):
        folder = Folder.objects.first()
        profiles = ProfileChannel.objects.filter(folder_name=folder)
        form = {
            'folder': Folder.objects.all(),
            'profiles': profiles
        }
        return render(request, self.template_name, form)
    
    def get_filename_from_url(self,url):
        parsed_url = urlparse(url)
        path = unquote(parsed_url.path)
        filename = path.split('/')[-1]
        return filename
    
    def post(self, request):
        action = request.POST.get('action')
        if action == 'add-image-video':
            print(action)
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


    def patch(self, request):
        input_data = {
        'title': request.POST.get('title'),
        'description': request.POST.get('description'),
        'keyword': request.POST.get('keywords'),
        'date_upload': request.POST.get('time_upload'),
        'time_upload': request.POST.get('date_upload'),
        'content': request.POST.get('text-content'),
        'video_image' : request.POST.get('video_image')
        }
        thumnail = request.FILES.get('input-Thumnail')
        json_text = request.POST.get('text_content_2')
        video_id = request.POST.get('id-video-render')
        video = VideoRender.objects.get(id=video_id)


        date_upload_datetime = datetime.strptime(input_data['date_upload'], '%Y-%m-%d')
        date_formatted = date_upload_datetime.strftime('%Y-%m-%d')
        if not video:
            return JsonResponse({'success': False, 'message': 'Video không tồn tại!'})

        if request.user.is_superuser:
            self.update_video_info(video, input_data, date_formatted, json_text, thumnail, video_id)
            return JsonResponse({'success': True, 'message': 'Cập nhật video thành công!'})

        is_edit_title = Count_Use_data.objects.filter(videoRender_id=video, creade_video=False, edit_title=True, edit_thumnail=False).first()
        is_edit_thumnail = Count_Use_data.objects.filter(videoRender_id=video, creade_video=False, edit_title=False, edit_thumnail=True).first()

        if (is_edit_title and is_edit_thumnail and is_edit_title.use != request.user and is_edit_thumnail.use != request.user):
            return JsonResponse({'success': False, 'message': 'Video đang được chỉnh sửa bởi người khác!'})

        if is_edit_title and is_edit_title.use != request.user and input_data['title'] != video.title and input_data['title'] and input_data['title'] != "Đang chờ cập nhật":
            return JsonResponse({'success': False, 'message': 'Tiêu đề đang được chỉnh sửa bởi người khác!'})

        if is_edit_thumnail and is_edit_thumnail.use != request.user and thumnail:
            return JsonResponse({'success': False, 'message': 'Ảnh thumnail đang được chỉnh sửa bởi người khác!'})
        
        if (is_edit_title and is_edit_thumnail and is_edit_title.use == request.user and is_edit_thumnail.use == request.user):
            video.description = input_data['description']
            video.keywords = input_data['keyword']
            video.time_upload = input_data['time_upload']
            video.date_upload = date_formatted
            video.text_content = input_data['content']
            if input_data['title'] != video.title and input_data['title'] and input_data['title'] != "Đang chờ cập nhật":
                video.title = input_data['title']
                video.save()
                is_edit_title.title = input_data['title']
                is_edit_title.save()
            if thumnail:
                video.url_thumbnail = self.handle_thumbnail(video, thumnail, video_id)
                video.save()
                is_edit_thumnail.url_thumnail = video.url_thumbnail
                is_edit_thumnail.save()
        elif is_edit_title and is_edit_title.use == request.user and input_data['title'] != video.title and input_data['title'] and input_data['title'] != "Đang chờ cập nhật":
            self.update_video_info(video, input_data, date_formatted, json_text, thumnail, video_id)
            is_edit_title.title = input_data['title']
            is_edit_title.save()
        elif is_edit_thumnail and is_edit_thumnail.use == request.user and thumnail:
            self.update_video_info(video, input_data, date_formatted, json_text, thumnail, video_id)
            is_edit_thumnail.url_thumnail = video.url_thumbnail
            is_edit_thumnail.save()
        else:
            self.update_video_info(video, input_data, date_formatted, json_text, thumnail, video_id)
            data = Count_Use_data.objects.create(
                use=request.user,
                videoRender_id=video,
                edit_thumnail=bool(thumnail),
                edit_title=not bool(thumnail),
                creade_video=False,
                title=input_data['title'],
                url_thumnail=video.url_thumbnail if thumnail else None
            )

        return JsonResponse({'success': True, 'message': 'Cập nhật video thành công!'})