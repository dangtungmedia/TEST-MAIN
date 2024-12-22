import yt_dlp,requests



def get_video_info(video_url):
    api_url = "https://iloveyt.net/proxy.php"
    form_data = {"url": video_url}

    try:
        response = requests.post(api_url, data=form_data, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "api" not in data or "mediaItems" not in data["api"]:
            raise ValueError("Invalid API response format")
        title = data["api"]["title"]
        mediaPreviewUrl = data["api"]["previewUrl"]
        mediaThumbnail = data["api"]["imagePreviewUrl"]
        return {
            "title": title,
            "preview_url": mediaPreviewUrl,
            "thumbnail_url": mediaThumbnail
        }
            
    except requests.RequestException as e:
        print(f"Network error: {e}")
        return None
    except ValueError as e:
        print(f"Data error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
    

# def get_video_info(video_url):
#     ydl_opts = {
#         'proxy': "http://ybwi2317:SHCwyr4821@193.160.223.70:59522",
#         'noplaylist': True,
        
#     }
#     try:
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             # Lấy metadata video
#             info_dict = ydl.extract_info(video_url, download=False)
            
#             if not info_dict:
#                 print("Không thể lấy thông tin video")
#                 return None
                
#             # Trích xuất thông tin cần thiết
#             video_data = {
#                 'title': info_dict.get('title', 'N/A'),
#                 'thumbnail': info_dict.get('thumbnail', 'N/A'),
#                 'download_url': info_dict.get('url', 'N/A')
#             } 
#             return video_data
        
#     except Exception as e:
#         print(f"Lỗi chi tiết: {type(e).__name__}: {str(e)}")
#         return None

# # Test code
video_url = "https://www.youtube.com/watch?v=Kt0ty1DX8ks"
# video_info = get_video_info(video_url)

# if video_info:
#     print("\nThông tin video:")
#     print(f"Tiêu đề: {video_info['title']}")
#     print(f"Ảnh thumbnail: {video_info['thumbnail']}")
#     print(f"URL tải về: {video_info['download_url']}")
# else:
#     print("Không thể lấy thông tin video.")
    
    
result = get_video_info(video_url)

download_url = result["preview_url"]
if not download_url:
    print("xxxxxxxxxxxx")