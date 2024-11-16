

import yt_dlp

# Tùy chọn cấu hình yt-dlp với cookie
ydl_opts = {
    'cookiefile': 'cookie_youtube.txt',  # Đường dẫn tới tệp cookie
    'outtmpl': '%(title)s.%(ext)s',      # Đặt tên tệp tải về
    'quiet': False,                      # Hiển thị thông tin chi tiết khi tải
}

# URL của video YouTube
video_url = "https://www.youtube.com/watch?v=u0Ptw0r0Pq0"

try:
    # Tải video
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])
    print("Tải video hoàn tất!")
except Exception as e:
    print(f"Đã xảy ra lỗi: {e}")
