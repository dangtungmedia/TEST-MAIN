
import urllib


def get_filename_from_url(url):
    parsed_url = urllib.parse.urlparse(url)
    path = parsed_url.path
    filename = path.split('/')[-1]
    return filename



def process_video_segment(data, text_entry, data_sub, i, video_id, task_id, worker_id):
    """Hàm tạo video cho một đoạn văn bản."""
    try:
        # Tính thời lượng của đoạn video
        if data.get('file-srt'):
            start_time, end_time = data_sub[i]
            duration = convert_to_seconds(end_time) - convert_to_seconds(start_time)
        else:
            duration = get_audio_duration(f'media/{video_id}/voice/{text_entry["id"]}.wav')

        # Kiểm tra nếu thời lượng âm thanh không hợp lệ
        if duration <= 0:
            raise ValueError(f"Invalid duration calculated: {duration} for text entry {text_entry['id']}")

        out_file = f'media/{video_id}/video/{text_entry["id"]}.mp4'
        file = get_filename_from_url(text_entry.get('url_video', ''))
        
        # Kiểm tra đường dẫn file
        if not file:
            raise FileNotFoundError(f"File not found for URL: {text_entry.get('url_video')}")
        
        path_file = f'media/{video_id}/image/{file}'

        # Kiểm tra loại file
        file_type = check_file_type(path_file)
        if file_type not in ["video", "image"]:
            raise ValueError(f"Unsupported file type: {file_type} for {path_file}")

        # Xử lý video hoặc ảnh
        if file_type == "video":
            cut_and_scale_video_random(path_file, out_file, duration, 1920, 1080, 'video_screen')
        elif file_type == "image":
            random_choice = random.choice([True, False])
            if random_choice:
                image_to_video_zoom_in(path_file, out_file, duration, 1920, 1080, 'video_screen')
            else:
                image_to_video_zoom_out(path_file, out_file, duration, 1920, 1080, 'video_screen')
                
        return True
    except FileNotFoundError as e:
        print(f"File error: {e}")
        return False
    except ValueError as e:
        print(f"Value error: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False
    
    
    
update_status_video("Đang Render : Chuẩn bị tạo video", data['video_id'], task_id, worker_id)
video_id = data.get('video_id')
text = data.get('text_content')
create_or_reset_directory(f'media/{video_id}/video')

# Tải và kiểm tra nội dung văn bản
text_entries = json.loads(text)
total_entries = len(text_entries)