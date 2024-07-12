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

from .serializers import RenderSerializer,FolderSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.render.cace_database import get_video_render_data_from_cache, update_video_render_data_from_cache, get_Data_Text_Video_data_from_cache, get_count_use_data_from_cache
    

class FolderViewSet(viewsets.ModelViewSet):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

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