# import os
# from celery import shared_task
# from .models import VideoProfile
# from core.DropboxStorage import MyDropboxClient
# from django.conf import settings
# import shutil
# import cloudinary.uploader
# from django.core.files.storage import default_storage

# @shared_task
# def uploadfile_droxbox(videoId, file_path,filename):
#     video = VideoProfile.objects.get(id=videoId)
#     client = MyDropboxClient()
#     print(client.access_token)
#     try:
#         if video.video:
#             is_active = client.delete_file(video.video)
#             if is_active:
#                 print('delete file')
#         client.create_folder(videoId)
#         is_upload = client.upload_file(file_path,f'{videoId}/{filename}')
#         if is_upload:
#             video.video = f'{videoId}/{filename}'
#             dir_path = os.path.join(settings.MEDIA_ROOT, videoId)
#             if os.path.exists(dir_path):
#                 shutil.rmtree(dir_path)
#                 print(f'Thư mục "{videoId}" và tất cả nội dung bên trong đã được xóa.')
#             else:
#                 print(f'Thư mục "{videoId}" không tồn tại.')

#         if video.title !='Đang chờ cập nhật' and "Lỗi Upload" not in video.status_video and "Đang Upload" not in video.status_video:
#             if not video.img_thumbnail and not video.video:
#                 video.status_video = "Đang chờ cập nhật : Đã Xong Tiêu đề Chờ cập nhật Thumnail & Video"

#             if not video.img_thumbnail and video.video:
#                 video.status_video = "Đang chờ cập nhật : Đã Xong Tiêu đề & Video  Chờ cập nhật Thumnail"

#             elif video.img_thumbnail and not video.video:
#                 video.status_video = "Đang chờ cập nhật : Đã Xong Tiêu đề & Thumnail Chờ cập nhật Video"

#             elif video.img_thumbnail and video.video:
#                 video.status_video = "Đã cập nhật Xong : Chờ Upload Video"
#         elif "Lỗi Upload" not in video.status_video and "Đang Upload" not in video.status_video:
#             if not video.img_thumbnail and not video.video:
#                 video.status_video = "Đang chờ cập nhật : Tiêu đề & Thumnail & Video"

#             elif not video.img_thumbnail and video.video:
#                 video.status_video = "Đang chờ cập nhật : Đã Xong Video Chờ cập nhật Tiêu đề & Thumnail"

#             elif video.img_thumbnail and not video.video:
#                 video.status_video = "Đang chờ cập nhật : Đã Xong Thumnail Chờ cập nhật Tiêu đề & Video"

#             elif video.img_thumbnail and video.video:
#                 video.status_video = "Đang chờ cập nhật : Đã Xong Thumnail & Video Chờ cập nhật Tiêu đề"
#         video.save()
#     except Exception as e:
#         print(f"Error: {e}")
    
# @shared_task
# def upload_file_image_drobox(videoId, file_path,filename):
#     cloudinary.config(
#     cloud_name="dyirrnurp",
#     api_key="463473229769324",
#     api_secret="jVyuAfglCbj-04AfurqAOlg4ewg"
#     )
#     video = VideoProfile.objects.get(id=videoId)
#     try:
#         if video.img_thumbnail:
#             url_parts = video.img_thumbnail.split('/')
#             public_id = '/'.join(url_parts[-2:])
#             public_id_without_extension = public_id.split('.')[0]
#             cloudinary.uploader.destroy(public_id_without_extension)
#         file_path = default_storage.path(file_path)
#         result = cloudinary.uploader.upload(file_path, folder="uploads")
#         if result:
#             video.img_thumbnail = result['secure_url']
#             dir_path = os.path.join(settings.MEDIA_ROOT, videoId)
#             if os.path.exists(dir_path):
#                 shutil.rmtree(dir_path)
#                 print(f'Thư mục "{videoId}" và tất cả nội dung bên trong đã được xóa.')
#             else:
#                 print(f'Thư mục "{videoId}" không tồn tại.')
#         if video.title !='Đang chờ cập nhật' and ("Lỗi Upload" not in video.status_video or "Đang Upload" not in video.status_video):
#             if not video.img_thumbnail and not video.video:
#                 video.status_video = "Đang chờ cập nhật : Đã Xong Tiêu đề Chờ cập nhật Thumnail & Video"

#             if not video.img_thumbnail and video.video:
#                 video.status_video = "Đang chờ cập nhật : Đã Xong Tiêu đề & Video  Chờ cập nhật Thumnail"

#             elif video.img_thumbnail and not video.video:
#                 video.status_video = "Đang chờ cập nhật : Đã Xong Tiêu đề & Thumnail Chờ cập nhật Video"

#             elif video.img_thumbnail and video.video:
#                 video.status_video = "Đã cập nhật Xong : Chờ Upload Video"

#         elif "Lỗi Upload" not in video.status_video or "Đang Upload" not in video.status_video:
#             if not video.img_thumbnail and not video.video:
#                 video.status_video = "Đang chờ cập nhật : Tiêu đề & Thumnail & Video"

#             elif not video.img_thumbnail and video.video:
#                 video.status_video = "Đang chờ cập nhật : Đã Xong Video Chờ cập nhật Tiêu đề & Thumnail"

#             elif video.img_thumbnail and not video.video:
#                 video.status_video = "Đang chờ cập nhật : Đã Xong Thumnail Chờ cập nhật Tiêu đề & Video"

#             elif video.img_thumbnail and video.video:
#                 video.status_video = "Đang chờ cập nhật : Đã Xong Thumnail & Video Chờ cập nhật Tiêu đề"
#         video.save()
#     except Exception as e:
#         print(f"Error: {e}")