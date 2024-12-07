from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, JSONParser
from django.core.files.storage import default_storage
from apps.render.models import VideoRender
from apps.home.models import ProfileChannel
from django.http import JsonResponse
import os, shutil,urllib,random,subprocess,json,requests,io
from django.http import FileResponse, HttpResponseBadRequest
from datetime import datetime
from celery.result import AsyncResult
from django.db.models import Q

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
            task_id = request.data.get('task_id')
            worker_id = request.data.get('worker_id')
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
                    # Tạo đường dẫn tới thư mục dựa trên video_id
                    directory = f"data/{video.id}/"
                    
                    # Kiểm tra và tạo thư mục nếu chưa tồn tại
                    if not os.path.exists(directory):
                        os.makedirs(directory, exist_ok=True)
                        
                    file_path = f"data/{video.id}/{file_obj.name}"
                    if os.path.exists(file_path):
                        default_storage.delete(file_path)
                        print(f"Đã xóa tệp cũ: {file_path}")

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
            
        elif action == "update_status_celery":
            videos_in_progress = VideoRender.objects.filter(
                Q(status_video__icontains="Đang Render") | 
                Q(status_video__icontains="Đang Chờ Render")
            )
            for video in videos_in_progress:
                task_id = video.task_id
                if task_id:
                    result = AsyncResult(task_id)
                    if result.status == 'FAILURE':
                        status_video = "Render Lỗi: lỗi render"
                        video.status_video = status_video
                        video.save()   
                    # Lấy thời gian hiện tại
                    current_time = datetime.now()
                    task_duration = current_time - video.task_start_time
                    if task_duration.total_seconds() > 4 * 60 * 60:  # 4 giờ = 14400 giây
                        status_video = "Render Lỗi: lỗi render"
                        video.status_video = status_video
                        video.save()
                else:
                    status_video = "Render Lỗi: lỗi kiểm tra task_id"
                    video.status_video = status_video
                    video.save()
            return Response({"message": "Trạng thái video cập nhật thành công"}, status=200)
        

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
            url_thumbnail = request.data.get('thumbnail_url')

            print("xxxxxx")
            print(url_thumbnail)
            try:
                video = VideoRender.objects.get(id=video_id)
                video.title = title
                video.description = description
                video.url_thumbnail = url_thumbnail
                video.save()
                return Response({"message": "Video updated successfully"}, status=200)
            except VideoRender.DoesNotExist:
                return Response({"error": "Video not found"}, status=404)
            
        elif action == "get-video-backrought":
            video_directory = "video"  # Thay thế bằng đường dẫn thật đến thư mục video
            max_attempts = 1000  # Giới hạn số lần thử
            attempts = 0  # Đếm số lần thử

            while attempts < max_attempts:
                # Lấy danh sách các tệp video từ thư mục
                all_videos = self.get_video_list(video_directory)

                # Kiểm tra nếu không có video nào trong thư mục
                if not all_videos:
                    return HttpResponseBadRequest("Không có tệp video nào trong thư mục.")
                
                # Lấy danh sách video đã gửi trong yêu cầu (để không chọn lại)
                list_video = request.data.get('list_video', [])
                if not isinstance(list_video, list):
                    return HttpResponseBadRequest("list_video phải là một danh sách các tên tệp video.")

                # Lấy thời lượng yêu cầu (phải là một số)
                try:
                    duration = float(request.data.get('duration', 0))  # Đảm bảo duration là số
                except ValueError:
                    return HttpResponseBadRequest("duration phải là một số hợp lệ.")

                # Loại bỏ các video đã có trong list_video khỏi danh sách all_videos
                available_videos = [video for video in all_videos if video not in list_video]

                # Kiểm tra xem còn video nào để chọn không
                if not available_videos:
                    return HttpResponseBadRequest("Không còn video nào khác để chọn.")

                # Chọn ngẫu nhiên một video từ danh sách còn lại
                random_file = random.choice(available_videos)

                # Tính thời lượng của video
                video_path = os.path.join(video_directory, random_file)
                video_duration = self.get_video_duration(video_path)

                if duration == 0:
                    # Trả về phản hồi để tải tệp video
                    response = FileResponse(open(video_path, 'rb'), as_attachment=True, filename=random_file)
                    return response

                # Kiểm tra nếu thời lượng video nhỏ hơn duration và không nằm trong danh sách đã có
                if video_duration > duration:
                    # Trả về phản hồi để tải tệp video
                    response = FileResponse(open(video_path, 'rb'), as_attachment=True, filename=random_file)
                    return response
                # Tăng số lần thử
                attempts += 1

            # Nếu vượt quá số lần thử mà vẫn không tìm được video phù hợp
            return HttpResponseBadRequest("Không tìm thấy video nào phù hợp sau {} lần thử.".format(max_attempts))
        
        return Response({"message": "Invalid action"}, status=400)
    
    
    

    def get_video_duration(self, file_path):
        command = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=duration",
        "-of", "json",
            file_path
        ]
        
        # Chạy lệnh ffprobe và lấy đầu ra
        result = subprocess.run(command, capture_output=True, text=True)
        
        # Chuyển đổi đầu ra từ JSON thành dictionary
        result_json = json.loads(result.stdout)
        
        # Lấy thời lượng từ dictionary
        duration = float(result_json['streams'][0]['duration'])
        
        return duration
    

    def get_video_list(self, directory):
        # Lấy danh sách tất cả các tệp video trong thư mục
        file_list = os.listdir(directory)
        
        # Các định dạng video mà bạn mong muốn
        video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.flv']
        
        # Lọc ra các tệp có đuôi mở rộng là video
        video_files = [file for file in file_list if os.path.splitext(file)[1].lower() in video_extensions]
        
        return video_files
    
    
    
######

@app.task(bind=True, ignore_result=True, name='check_worker_status', queue='check_worker_status')
def check_worker_status(self, *args, **kwargs):
    data = {
        'secret_key': 'ugz6iXZ.fM8+9sS}uleGtIb,wuQN^1J%EvnMBeW5#+CYX_ej&%',
        'action': 'update_status_celery'
    }
    url = f'http://daphne:5505/api/'
    response = requests.post(url, json=data)
    if response.status_code == 200:
        print("Trạng thái video đã được cập nhật thành công.")
    else:
        print(f"Lỗi cập nhật trạng thái video: {response.status_code}")
        
        
######