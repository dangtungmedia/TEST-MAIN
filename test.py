import yt_dlp

proxy_url = "http://ybwi2317:SHCwyr4821@193.160.223.70:59522"  

ydl_opts = {
    'proxy': proxy_url,
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',  # Sửa format
    'quiet': True,
    'noplaylist': True
}

video_url = "https://www.youtube.com/watch?v=HF1syyQGNYw"

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Lấy thông tin video
        info = ydl.extract_info(video_url, download=False)
        formats = info.get('formats', [])

        # Tìm URL phù hợp từ danh sách formats
        for format in formats:
            # In ra để kiểm tra các format có sẵn
            print(f"Format ID: {format.get('format_id')} - {format.get('ext')} - {format.get('format_note', '')}")
            
            # Lấy URL từ format phù hợp
            if format.get('ext') == 'mp4' and 'video' in format.get('format_note', '').lower():
                playable_url = format['url']
                break
        else:
            playable_url = None

        result = {
            'title': info.get('title', ''),
            'url': playable_url,
            'thumbnail': info.get('thumbnail', '')
        }
        print("\nKết quả:")
        print(result)

except Exception as e:
    print(f"Error: {str(e)}")