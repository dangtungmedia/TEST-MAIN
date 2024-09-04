from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, JSONParser
from django.core.files.storage import default_storage
from apps.render.models import VideoRender
from apps.home.models import ProfileChannel
from django.http import JsonResponse
import os, shutil,urllib

class ApiApp(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, JSONParser]


    def get_filename_from_url(self,url):
        parsed_url = urllib.parse.urlparse(url)
        path = parsed_url.path
        filename = path.split('/')[-1]
        return filename
    

    def post(self, request, id=None):
        secret_key = request.data.get('secret_key')
        action = request.data.get('action')

        if secret_key != "ugz6iXZ.fM8+9sS}uleGtIb,wuQN^1J%EvnMBeW5#+CYX_ej&%":
            return Response({"error": "Invalid secret key"}, status=403)

        if action == "update_status":
            video_id = request.data.get('video_id')
            status = request.data.get('status')
            try:
                video = VideoRender.objects.get(id=video_id)
                video.status_video = status
                video.save()
                if status == "Upload VPS Thành Công":
                    file_name = self.get_filename_from_url(video.url_video)
                    url = "data/" + str(video.id) + "/" + file_name
                    default_storage.delete(url)
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

        elif action == "upload-video-to-vps":
            ip_vps = request.data.get('ip_vps')
            channel_name = request.data.get('channel_name')
            
            try:
                # Tìm profile với ip_vps và channel_name
                profile = ProfileChannel.objects.get(channel_vps_upload=ip_vps, channel_name=channel_name)
                
                # Kiểm tra xem chuỗi "Render Thành Công" có nằm trong status_video của bất kỳ video nào
                video_exists = VideoRender.objects.filter(profile_id=profile.id, status_video__icontains="Render Thành Công").exists()
                
                if video_exists:
                    video = VideoRender.objects.filter(profile_id=profile.id, status_video__icontains="Render Thành Công").first()
                    data = {
                        "video_id": video.id,
                        "video_url": video.url_video,
                        'url_thumbnail': video.url_thumbnail,
                        'title': video.title,
                        'description': video.description,
                        'keywords': video.keywords,
                        'time_upload': video.time_upload,
                        'date_upload': video.date_upload,
                    }
                    return Response(data)
                else:
                    return Response({"message": "Không tìm thấy video  Render Thành Công ..."}, status=404)

            except ProfileChannel.DoesNotExist:
                return Response({"message": f"Không tìm thấy Profile {channel_name} có IP {ip_vps}! Vui Lòng Kiểm Tra Lại IP Hoặc Tên Profile cho Chính Xác"}, status=404)
            
            except Exception as e:
                return Response({"message": str(e)}, status=500)
        

        elif action == "get-audio-voicevox":
            voice_id = request.json.get('voice_id')
            text = request.json.get('text_voice')

            # Lấy cấu hình âm thanh
            url_query = f"http://127.0.0.1:50021/audio_query?speaker={voice_id}"
            response_query = requests.post(url_query, params={'text': text})
            response_query.raise_for_status()
            query_json = response_query.json()

            # Thay đổi giá trị speedScale trong cấu hình
            query_json["speedScale"] = 1.0

            # Tạo tệp âm thanh với cấu hình đã thay đổi
            url_synthesis = f"http://127.0.0.1:50021/synthesis?speaker={voice_id}"
            headers = {"Content-Type": "application/json"}
            response_synthesis = requests.post(url_synthesis, headers=headers, json=query_json)
            response_synthesis.raise_for_status()

            # Trả về tệp âm thanh trực tiếp từ bộ nhớ
            audio_file = io.BytesIO(response_synthesis.content)
            return send_file(audio_file, mimetype='audio/wav', as_attachment=True, download_name='output_audio.wav')


        elif action == "update-info-video":
            video_id = request.data.get('video_id')
            title = request.data.get('title')
            description = request.data.get('title')
            url_thumbnail = request.data.get('url_thumbnail')
            try:
                video = VideoRender.objects.get(id=video_id)
                video.title = title
                video.description = description
                video.url_thumbnail = url_thumbnail
                video.save()
                return Response({"message": "Video updated successfully"})
            except VideoRender.DoesNotExist:
                return Response({"error": "Video not found"}, status=404)

        return Response({"message": "Invalid action"}, status=400)

