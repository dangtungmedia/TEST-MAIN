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
        action = data.get('action')
        if secret_key != "ugz6iXZ.fM8+9sS}uleGtIb,wuQN^1J%EvnMBeW5#+CYX_ej&%":
            return Response({"error": "Invalid secret key"}, status=403)
        elif action == "update_status":
            video = VideoRender.objects.get(id=video_id)
            video.status_video = status
            video.task_id = task_id
            video.worker_id = worker_id
            video.save()
            return Response({"message": "Hello, world!"})
        elif action == "upload":
            video = VideoRender.objects.get(id=video_id)
            video.task_id = task_id
            video.worker_id = worker_id
            file_obj = request.FILES['file']
            if file_obj:
                file_image = default_storage.save(f"data/{video.id}/{file_obj}", file_obj)
                file_url = default_storage.url(file_image)
                video.file_video = file_url
            video.save()
            return Response({"message": "Hello, world!"})
        
        