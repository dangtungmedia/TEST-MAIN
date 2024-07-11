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

from apps.render.cace_database import get_video_render_data_from_cache, update_video_render_data_from_cache, get_Data_Text_Video_data_from_cache, get_count_use_data_from_cache
from apps.home.models import Voice_language, syle_voice,ProfileChannel
from apps.render.models import VideoRender
import json

class ApiApp(APIView):
    permission_classes = [AllowAny]  # Cho phép mọi request không cần đăng nhập
    def post(self, request, id):
        data = json.loads(request.body)
        video_id = data.get('video_id')
        status = data.get('status')
        task_id = data.get('task_id')
        worker_id = data.get('worker_id')
        secret_key = data.get('secret_key')
        if secret_key != "ugz6iXZ.fM8+9sS}uleGtIb,wuQN^1J%EvnMBeW5#+CYX_ej&%":
            return Response({"error": "Invalid secret key"}, status=403)

        else:
            video = VideoRender.objects.get(id=video_id)
            video.status_video = status
            video.task_id = task_id
            video.worker_id = worker_id
            video.save()
            update_video_render_data_from_cache(video.id)
            return Response({"message": "Hello, world!"})