import os
import time
import yt_dlp






def downdload_video_reup(data, task_id, worker_id):
    video_id = data.get('video_id')
    output_file = f'media/{video_id}/cache.mp4'
    url = data.get('url_video_youtube')
    max_retries = 3  # Số lần thử lại
    retry_delay = 5  # Thời gian chờ giữa các lần thử (giây)
    video_title = None  # Biến lưu tiêu đề video

    # Lấy proxy từ môi trường (nếu có)
    proxy_url = os.environ.get('PROXY_URL')  # Thay đổi proxy ở đây nếu cần

    # Cấu hình yt-dlp
    ydl_opts = {
        # 'proxy': proxy_url,  # Cấu hình proxy
        'format': 'bestvideo[height=720]+bestaudio/best',
        'outtmpl': f"{output_file}",
        'merge_output_format': 'mp4',  # Hợp nhất video và âm thanh thành định dạng MP4
        # 'progress_hooks': [progress_hook],  # Thêm hàm xử lý tiến trình
    }

    for attempt in range(max_retries):
        try:
            # Khởi tạo yt-dlp
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"Thử tải video (lần {attempt + 1}) từ: {url}")

                # Lấy thông tin video
                video_info = ydl.extract_info(url, download=False)  # Chỉ lấy thông tin, không tải video
                video_title = video_info.get('title', 'Không xác định')  # Lấy tiêu đề video
                print(f"Tiêu đề video: {video_title}")

                # Tiến hành tải video
                ydl.download([url])

            # Cập nhật trạng thái sau khi tải xong
            update_status_video(f"Đang Render : Đã tải xong video", video_id, task_id, worker_id)
            return video_title  # Trả về tiêu đề video nếu tải thành công

        except yt_dlp.DownloadError as e:
            print(f"Lỗi khi tải video từ {url} (lần {attempt + 1}): {str(e)}")
        
        except Exception as e:
            print(f"Lỗi không xác định khi tải video từ {url} (lần {attempt + 1}): {str(e)}")

        # Chờ trước khi thử lại (nếu không phải lần cuối)
        if attempt < max_retries - 1:
            print(f"Chờ {retry_delay} giây trước khi thử lại...")
            time.sleep(retry_delay)

    # Nếu thử đủ số lần mà vẫn lỗi, trả về None
    final_error_message = "Render Lỗi: Không thể tải video sau nhiều lần thử."
    print(final_error_message)
    return None
