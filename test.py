import re

def get_youtube_thumbnail(youtube_url):
    try:
        # Regex pattern để lấy video ID
        pattern = r'(?:https?:\/{2})?(?:w{3}\.)?youtu(?:be)?\.(?:com|be)(?:\/watch\?v=|\/)([^\s&]+)'
        video_id = re.findall(pattern, youtube_url)[0]
        
        # Tạo các URL thumbnail
        thumbnails = {
            'max': f'https://i3.ytimg.com/vi/{video_id}/maxresdefault.jpg',
            'hq': f'https://i3.ytimg.com/vi/{video_id}/hqdefault.jpg',
            'mq': f'https://i3.ytimg.com/vi/{video_id}/mqdefault.jpg',
            'sd': f'https://i3.ytimg.com/vi/{video_id}/sddefault.jpg',
            'default': f'https://i3.ytimg.com/vi/{video_id}/default.jpg'
        }
        
        return thumbnails
        
    except Exception as e:
        return f"Error: {str(e)}"

# Sử dụng
url = "https://www.youtube.com/watch?v=iGo66QkzeSY"
thumbnails = get_youtube_thumbnail(url)
print(f"Max quality: {thumbnails['max']}")
