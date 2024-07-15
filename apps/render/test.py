from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
import json
from asgiref.sync import async_to_sync
from .models import VideoRender
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer


@receiver(post_save, sender=VideoRender)
def notify_video_change(sender, instance, **kwargs):
    # Lấy layer kênh
    channel_layer = get_channel_layer()
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

    room_name = instance.profile_id.id
    room_group_name = f"render_profile_{room_name}"
    # Gửi thông báo đến group
    async_to_sync(channel_layer.group_send)(
        room_group_name,
        {
            'type': 'video_change',
            'message': 'oki oki'
        }
    )

class RenderConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"render_profile_{self.room_name}"

        print("xxxxxxxxxxxxxxxxxxxxx connect")


        # Thêm kênh vào group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):

        print("xxxxxxxxxxxxxxxxxxxxx group_discard")

        # Loại bỏ kênh khỏi group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def get_video_data(self):
        videos = VideoRender.objects.filter(profile_id=self.room_name)
        data = [
            {
                'id': video.id,
                'title': video.title,
                'status': video.status_video,
                'url_thumbnail': video.url_thumbnail if video.url_thumbnail else "/static/assets/img/no-image-available.png",
                'time_upload': video.time_upload,
                'date_upload': video.date_upload,
            } for video in videos
        ]
        return data


    def video_change(self, event):
        try:
            data = self.get_video_data()
            self.send(text_data=json.dumps(data))

            print("xxxxxxxxxxxxxxxxxxxxx send group")
        except Exception as e:
            self.send(text_data=json.dumps({"error": "An error occurred when processing video change event!"}))

def patch(self, request):
        input_data = {
        'title': request.GET.get('title'),
        'description': request.GET.get('description'),
        'keyword': request.GET.get('keywords'),
        'date_upload': request.GET.get('time_upload'),
        'time_upload': request.GET.get('date_upload'),
        'content': request.GET.get('text-content'),
        'video_image': request.GET.get('video_image')
        }
        thumnail = request.FILES.get('input-Thumnail')
        json_text = request.GET.get('text_content_2')
        video_id = request.GET.get('id_video')
        try:
            video = VideoRender.objects.get(id=video_id)
        except VideoRender.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Video không tồn tại!'})

        date_upload_datetime = datetime.strptime(input_data['date_upload'], '%Y-%m-%d')
        date_formatted = date_upload_datetime.strftime('%Y-%m-%d')

        if request.user.is_superuser:
            self.update_video_info(video, input_data, date_formatted, json_text, thumnail, video_id)
            return JsonResponse({'success': True, 'message': 'Cập nhật video thành công!'})

        is_edit_title = Count_Use_data.objects.filter(videoRender_id=video, creade_video=False, edit_title=True, edit_thumnail=False).first()
        is_edit_thumnail = Count_Use_data.objects.filter(videoRender_id=video, creade_video=False, edit_title=False, edit_thumnail=True).first()

        # Kiểm tra nếu tiêu đề hoặc thumnail đang được chỉnh sửa bởi người khác
        if is_edit_title and is_edit_thumnail:
            if (is_edit_title.use != request.user and input_data['title'] != video.title and input_data['title'] and input_data['title'] != "Đang chờ cập nhật") or \
            (is_edit_thumnail.use != request.user and thumnail):
                return JsonResponse({'success': False, 'message': 'Video đang được chỉnh sửa bởi người khác!'})

        if is_edit_title and is_edit_title.use != request.user and input_data['title'] != video.title and input_data['title'] and input_data['title'] != "Đang chờ cập nhật":
            return JsonResponse({'success': False, 'message': 'Tiêu đề đang được chỉnh sửa bởi người khác!'})

        if is_edit_thumnail and is_edit_thumnail.use != request.user and thumnail:
            return JsonResponse({'success': False, 'message': 'Ảnh thumnail đang được chỉnh sửa bởi người khác!'})

        # Chỉ thêm vào bảng Count_Use_data nếu có sự thay đổi trong tiêu đề hoặc thumnail và người dùng hiện tại chưa thực hiện chỉnh sửa trước đó
        if (not is_edit_title or (is_edit_title and is_edit_title.use != request.user)) and input_data['title'] != video.title:
            Count_Use_data.objects.create(videoRender_id=video, creade_video=False, edit_title=True, edit_thumnail=False, use=request.user)

        if (not is_edit_thumnail or (is_edit_thumnail and is_edit_thumnail.use != request.user)) and thumnail:
            Count_Use_data.objects.create(videoRender_id=video, creade_video=False, edit_title=False, edit_thumnail=True, use=request.user)

        self.update_video_info(video, input_data, date_formatted, json_text, thumnail, video_id)
        return JsonResponse({'success': True, 'message': 'Cập nhật thành công!'})



$("#create_videos_news").click(function () {
        console.log('Create video news');
        $('#progress-bar-status').css('width', `${0}%`);
        const host = window.location.host;
        const protocol = window.location.protocol;
        const csrfToken = getCSRFToken();
        const profile_id = $('#channel_name').val();
        const fetchUrl = `${protocol}//${host}/profiles/${profile_id}/add_videos/`;

        let dateValue = $('#date-Input').val();
        const timeValue = $('#input-time-upload').val().split(',');

        const countVideos = parseInt($('#count-video').val()); // Lấy giá trị của input số lượng video và chuyển sang số nguyên
        $('#progress-bar-status').css('display', 'block'); // Hiển thị thanh tiến trình
        $('#cread-status-videos').text(`Đang tạo video ...1/${countVideos}`);
        let videosCreated = 0;
        let currentDate = dateValue; // Khởi tạo currentDate bằng giá trị dateValue

        for (let i = 0; i < countVideos; i++) {
            let currentTime = timeValue[videosCreated % timeValue.length];
            const videoData = {
                upload_time: currentTime,
                upload_date: currentDate
            };
            fetch(fetchUrl, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(videoData)
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    videosCreated++;
                    $('#cread-status-videos').text(`Đang tạo video ...${videosCreated}/${countVideos}`);
                    const progress = (videosCreated / countVideos) * 100;
                    $('#progress-bar-status').css('width', `${progress}%`);
                    $('#progress-bar-status').attr('aria-valuenow', progress);
                    if (videosCreated === countVideos) {
                        $('#cread-status-videos').text(`Đã tạo xong ${countVideos} video`);
                    }
                    console.log(data);
                })
                .catch(error => {
                    console.error('Error:', error);
                    $('#cread-status-videos').text(`Lỗi khi tạo video. Đã tạo được ${videosCreated} video.`);
                });

            // Nếu đã sử dụng hết các giá trị trong timeValue, tăng ngày lên
            if ((i + 1) % timeValue.length === 0) {
                currentDate = incrementDate(currentDate);
            }
        }

    });

    function incrementDate(dateStr) {
        let date = new Date(dateStr);
        date.setDate(date.getDate() + 1);
        return date.toISOString().split('T')[0]; // Chuyển đổi lại định dạng yyyy-mm-dd
    }