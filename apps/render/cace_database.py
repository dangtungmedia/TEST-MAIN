
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse

from apps.home.models import Folder, Font_Text, syle_voice, Voice_language, ProfileChannel
from .models import VideoRender, DataTextVideo, video_url,Count_Use_data,Api_Key_Azure

from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
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

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
import time


def get_video_render_data_from_cache():
    video_render_data = cache.get('VideoRender_cache')
    if video_render_data is not None:
        return video_render_data
    else:
        all_data = list(VideoRender.objects.values())
        cache.set('VideoRender_cache', all_data)
        return all_data
    
def update_video_render_data_from_cache(id):
    video_render_data = cache.get('VideoRender_cache')
    video = VideoRender.objects.get(id=id)
    if video_render_data is not None:
        for index, item in enumerate(video_render_data):
            if item['id'] == id:
                # Cập nhật dữ liệu mới vào cache
                video_render_data[index] = video.__dict__
                break
        cache.set('VideoRender_cache', video_render_data)
    else:
        # Nếu cache không tồn tại, tạo mới cache
        all_data = list(VideoRender.objects.values())
        cache.set('VideoRender_cache', all_data)



def get_Data_Text_Video_data_from_cache():
    video_url_data = cache.get('video_url_cache')
    if video_url_data is not None:
        return video_url_data
    else:
        all_data = list(DataTextVideo.objects.values())
        cache.set('video_url_cache', all_data)
        return all_data
    
def get_count_use_data_from_cache():
    count_use_data = cache.get('count_use_data_cache')
    if count_use_data is not None:
        return count_use_data
    else:
        all_data = list(Count_Use_data.objects.values())
        cache.set('count_use_data_cache', all_data)
        return all_data