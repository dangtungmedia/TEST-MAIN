from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, JSONParser
from django.core.files.storage import default_storage
from apps.render.models import VideoRender
from django.http import JsonResponse

class ApiApp(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, JSONParser]

    def post(self, request, id):
        secret_key = request.data.get('secret_key')
        action = request.data.get('action')

        if secret_key != "ugz6iXZ.fM8+9sS}uleGtIb,wuQN^1J%EvnMBeW5#+CYX_ej&%":
            return Response({"error": "Invalid secret key"}, status=403)

        if action == "update_status":
            video_id = request.data.get('video_id')
            status = request.data.get('status')
            task_id = request.data.get('task_id')
            worker_id = request.data.get('worker_id')

            try:
                video = VideoRender.objects.get(id=video_id)
                video.status_video = status
                video.task_id = task_id
                video.worker_id = worker_id
                video.save()
                return Response({"message": "Status updated successfully"})
            except VideoRender.DoesNotExist:
                return Response({"error": "Video not found"}, status=404)

        elif action == "upload":
            video_id = request.data.get('video_id')
            task_id = request.data.get('task_id')
            worker_id = request.data.get('worker_id')

            try:
                video = VideoRender.objects.get(id=video_id)
                video.task_id = task_id
                video.worker_id = worker_id

                file_obj = request.FILES.get('file')
                if file_obj:
                    file_path = f"data/{video.id}/{file_obj.name}"
                    file_video = default_storage.save(file_path, file_obj)
                    file_url = default_storage.url(file_video)
                    video.url_video = file_url
                video.save()
                return JsonResponse({'success': True, 'data': 'File uploaded and listed successfully'})

            except VideoRender.DoesNotExist:
                return Response({"error": "Video not found"}, status=404)

        return Response({"error": "Invalid action"}, status=400)