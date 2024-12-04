from random_video_effect import create_parallax_left_video,create_parallax_right_video,create_scrolling_image_video,create_zoom_in_video,create_zoom_out_video,create_zoom_in_video_with_background,create_zoom_out_video_with_background,random_video_effect_cython

import os
image_path = "media/8988/image/20.jpg"  # Set image path
out_path = "caches.mp4"  # Set output path
duration = 7.752  # Video duration (seconds)
fps = 30  # Frames per second
width = 1920  # Video width
height = 1080  # Video height
print("Creating video...")
# create_parallax_left_video(image_path, out_path, duration, fps, width, height)
# create_parallax_right_video(image_path, out_path, duration, fps, width, height)
# create_zoom_in_video(image_path, out_path, duration, fps, width, height)
# create_zoom_out_video(image_path, out_path, duration, fps, width, height)
# create_zoom_in_video_with_background(image_path, out_path, duration, fps, width, height)
# create_zoom_out_video_with_background(image_path, out_path, duration, fps, width, height)
# random_video_effect_cython(image_path, out_path, duration, fps, width, height)

def create_video_for_images(image_folder, out_folder, duration, fps, width, height):
    if not os.path.exists(out_folder):
        os.makedirs(out_folder, exist_ok=True)
    
    # Lặp qua từng ảnh trong thư mục image_folder
    for image_name in os.listdir(image_folder):
        image_path = os.path.join(image_folder, image_name)
        
        # Kiểm tra xem có phải là ảnh không
        if os.path.isfile(image_path) and image_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            print(f"Đang tạo video cho {image_path}...")

            # Tạo các video cho ảnh này theo nhiều hiệu ứng khác nhau
            out_path = os.path.join(out_folder, f"{os.path.splitext(image_name)[0]}_parallax_left.mp4")
            create_parallax_left_video(image_path, out_path, duration, fps, width, height)
            
            out_path = os.path.join(out_folder, f"{os.path.splitext(image_name)[0]}_zoom_in.mp4")
            create_zoom_in_video(image_path, out_path, duration, fps, width, height)
            
            out_path = os.path.join(out_folder, f"{os.path.splitext(image_name)[0]}_zoom_out.mp4")
            create_zoom_out_video(image_path, out_path, duration, fps, width, height)
            
            out_path = os.path.join(out_folder, f"{os.path.splitext(image_name)[0]}_parallax_right.mp4")
            create_parallax_right_video(image_path, out_path, duration, fps, width, height)
            
            # Tiếp tục với các hiệu ứng khác như zoom in with background, zoom out with background, ...
            out_path = os.path.join(out_folder, f"{os.path.splitext(image_name)[0]}_zoom_in_bg.mp4")
            create_zoom_in_video_with_background(image_path, out_path, duration, fps, width, height)
            
            out_path = os.path.join(out_folder, f"{os.path.splitext(image_name)[0]}_zoom_out_bg.mp4")
            create_zoom_out_video_with_background(image_path, out_path, duration, fps, width, height)
            
            print(f"Đã tạo tất cả video cho {image_name}")

# Thực thi
image_path = "media/8988/image/"  # Đường dẫn thư mục chứa ảnh
out_path = "output_videos"  # Thư mục đầu ra lưu video
duration = 7.752  # Thời gian video (giây)
fps = 30  # FPS video
width = 1920  # Chiều rộng video
height = 1080  # Chiều cao video

print("Bắt đầu tạo video từ ảnh...")
create_video_for_images(image_path, out_path, duration, fps, width, height)
