from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse

from apps.home.models import Folder, Font_Text, syle_voice, Voice_language, ProfileChannel
from .models import VideoRender, DataTextVideo, video_url,Count_Use_data,Api_Key_Azure,Api_Voice_ttsmaker

from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from pytube import YouTube
import json ,re ,random ,string
from datetime import datetime, timedelta
from django.core.files.storage import default_storage
from .forms import VideoForm
from urllib.parse import urlparse, unquote
from django.core.cache import cache
from PIL import Image
from io import BytesIO
from apps.login.models import CustomUser
import calendar
import os

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
import time

from apps.render.task import render_video
from celery.result import AsyncResult

from .serializers import RenderSerializer
from rest_framework import viewsets

from apps.render.cace_database import get_video_render_data_from_cache, update_video_render_data_from_cache, get_Data_Text_Video_data_from_cache, get_count_use_data_from_cache
    

class VideoRenderViewSet(viewsets.ModelViewSet):
    serializer_class = RenderSerializer
    
    def get_queryset(self):
        queryset = VideoRender.objects.none()
        folder_id = self.request.query_params.get('folder_id', None)
        profile_id = self.request.query_params.get('profile_id', None)
        if folder_id and profile_id:
            queryset = VideoRender.objects.filter(folder_id=folder_id, profile_id=profile_id)
        return queryset



class index(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    template_name = 'render/index.html'
    def get(self, request):
        folder = Folder.objects.first()

        profiles = ProfileChannel.objects.none()
        profile = None
        video_render = []

        if folder:
            profiles = ProfileChannel.objects.filter(folder_name=folder)
            profile = profiles.first()

            if profile:
                video_render = VideoRender.objects.filter(folder_id=folder.id, profile_id=profile.id)

        # Sử dụng Paginator để phân trang video_render
        paginator = Paginator(video_render, per_page=50)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        # Render các template
        video_html = render_to_string('render/video_show.html', {'page_obj': page_obj}, request)
        page_bar_html = render_to_string('render/page_bar_template.html', {'page_obj': page_obj}, request)
        
        current_time = timezone.now().strftime('%Y-%m-%d')

        # Chuẩn bị dữ liệu để truyền vào template
        form = {
            'folder': Folder.objects.all(),
            'profiles': profiles,
            'video_html': video_html,
            'page_bar_html': page_bar_html,
            'profile': profile,
            'current_time': current_time
        }
        return render(request, self.template_name, form)
    
    
    def check_video_url(self,url):
        match = re.match(r'https?://www\.youtube\.com/watch\?v=.+', url)
        if not match:
            return False, "Vui Lòng Nhập Đúng Url Video", None, None
        try:        
            yt = YouTube(url)

            channel_id = yt.channel_id

            url = yt.watch_url

            title = yt.title
            return True, url, channel_id, title
        except:
            return False, "Video Không Tồn Tại ", None, None
    
    def get_filename_from_url(self,url):
        parsed_url = urlparse(url)
        path = unquote(parsed_url.path)
        filename = path.split('/')[-1]
        return filename
    
    def post(self, request):
        action = request.POST.get('action')
        if action == 'add_video_text_content':
            try:
                is_valid, url,channel_id,title = self.check_video_url(request.POST.get('url'))
                if is_valid:
                    is_url = video_url.objects.filter(url=url).exists()
                    if is_url:
                        return JsonResponse({'success': False, 'message': 'Video đã tồn tại không thể thêm tiếp !'})
                    else:
                        video = DataTextVideo.objects.create(
                            folder_id=Folder.objects.get(id=request.POST.get('folder_id')),
                            url_video=url,
                            count_text=len(request.POST.get('content')),
                            id_channel=channel_id,
                            title=title,
                            text_video= request.POST.get('content')
                        )
                        return JsonResponse({'success': True, 'message': "Thêm url thành công rồi nhé !"})
                else:
                    return JsonResponse({'success': False, 'message': url})
            except Exception as e:
                return JsonResponse({'success': False, 'message': str(e)})
            


        elif action == 'add_videos':
            folder_id = request.POST.get('folder_name')
            profile_id = request.POST.get('channel_name')

            count_video = request.POST.get('count_video')
            count_text_video = request.POST.get('count_text_video')
            date_upload = request.POST.get('date_upload')
            time_upload = request.POST.get('time_upload')

            all_video = VideoRender.objects.all().values()

            url_video = video_url.objects.filter(profile_id=profile_id).values()

            video_profile_urls = {item['url'] for item in url_video}
        
            filtered_videos = [video for video in all_video if video.get('url_video') not in video_profile_urls and video.get('url_video')]

            list_news = []
            selected_urls = set()

            if len(filtered_videos) < int(count_video) :
                return JsonResponse({'success': False, 'message': 'Không đủ video để tạo ui lòng nhập thêm link video!'})
            
            for _ in range(int(count_video)):
                item_video = []
                total_text_count = 0  

                while total_text_count < int(count_text_video):
                    choice = random.choice(filtered_videos) 
                    choice_url = choice.get('url_video') 

                    
                    if choice_url not in video_profile_urls and choice_url not in selected_urls:
                        selected_urls.add(choice_url) 
                        item_video.append(choice) 
                        total_text_count += int(choice.get('count_text'))  

                        
                        if total_text_count >= int(count_text_video):
                            break 
                list_news.append(item_video)

            date_upload = datetime.strptime(date_upload, '%Y-%m-%d').date()
            time_slot_index = 0
            time_slots = time_upload.split(',') 
            selected_videos = []
            for videos in list_news:
                count = 1
                text_video = ""
                for video in videos:
                    text_video += f"\n------------------------------- Tin {count} ------------------------------------------\n\n "
                    text_video +=  f'Url video {video.get("url_video")} \n\n'
                    text_video +=  f'-----------------------------------------------------------------------------------------\n\n'
                    text_video += video.get('text_video')
                    video_url.objects.create(
                        folder_id=Folder.objects.get(id=folder_id),
                        profile_id=ProfileChannel.objects.get(id=profile_id),
                        url=video.get('url_video')
                    )
                    count += 1
                current_time_slot = time_slots[time_slot_index]
                date_upload_str = date_upload.strftime('%Y-%m-%d')
                time_upload_str = current_time_slot
                profile = ProfileChannel.objects.get(id=profile_id)
                font_text = profile.channel_font_text

                data = VideoRender.objects.create(
                    folder_id = Folder.objects.get(id=folder_id),
                    profile_id = profile ,
                    name_video = ''.join(random.choices(string.ascii_letters + string.digits, k=7)),
                    url_video_youtube = [url["id"] for url in videos],
                    text_content = text_video,
                    title='Đang chờ cập nhật',
                    description= profile.channel_description,
                    keywords= profile.channel_keywords,

                    time_upload=time_upload_str,
                    date_upload=date_upload_str,
                    status_video= "Đang Chờ Cập Nhật Tiêu Đề & Thumnail !",
                    is_render_start = False,

                    intro_active = profile.channel_intro_active,
                    intro_url = profile.channel_intro_url,
                    outro_active = profile.channel_outro_active,
                    outro_url = profile.channel_outro_url,
                    logo_active = profile.channel_logo_active,
                    logo_url = profile.channel_logo_url,
                    logo_position = profile.channel_logo_position,
                    font_text = font_text.font_name,

                    font_size = profile.channel_font_size,
                    font_bold = profile.channel_font_bold,
                    font_italic = profile.channel_font_italic,
                    font_underline = profile.channel_font_underline,
                    font_strikeout = profile.channel_font_strikeout,

                    font_color = profile.channel_font_color,
                    font_color_opacity = profile.channel_font_color_opacity,
                    font_color_troke = profile.channel_font_color_troke,
                    font_color_troke_opacity = profile.channel_font_color_troke_opacity,

                    stroke_text = profile.channel_stroke_text,
                    font_background = profile.channel_font_background,
                    channel_font_background_opacity = profile.channel_font_background_opacity,

                    voice = profile.channel_voice,
                    voice_style = profile.channel_voice_style,
                    voice_speed = profile.channel_voice_speed,
                    voice_pitch = profile.channel_voice_pitch,
                    voice_volume = profile.channel_voice_volume,
                        )
                time_slot_index += 1
                if time_slot_index >= len(time_slots):
                    time_slot_index = 0
                    date_upload += timedelta(days=1)

            return JsonResponse({'success': True, 'message': 'TThêm video thành công !'})
        
        elif action == 'add_one_video':
            folder_name = request.POST.get('folder_name')
            channel_name = request.POST.get('channel_name')
            title = request.POST.get('input-title')
            description = request.POST.get('input-description')
            keyword = request.POST.get('input-keyword')
            date_upload = request.POST.get('input-date-upload')
            time_upload = request.POST.get('input-time-upload')
            content = request.POST.get('input-text-content')
            thumnail = request.FILES.get('input-Thumnail')
            video_id = request.POST.get('id-video-edit')
            date_upload_datetime = datetime.strptime(date_upload, '%Y-%m-%d')
            date_formatted = date_upload_datetime.strftime('%Y-%m-%d')
            profile = ProfileChannel.objects.get(id=channel_name)
            font_text = profile.channel_font_text
            if title == '':
                return JsonResponse({'success': False, 'message': 'Vui lòng nhập tiêu đề!'})
            
            if time_upload == '':
                return JsonResponse({'success': False, 'message': 'Vui lòng nhập thời gian upload!'})

            time_parts = time_upload.split(":")
            minutes = int(time_parts[1])
            if minutes not in [0, 15, 30, 45]:
                return JsonResponse({'success': False, 'message': 'Thời gian upload không hợp lệ!\n Thời gian upload phải là 0, 15, 30 hoặc 45 phút!'})

            if profile and video_id in ['none', '']:
                video = VideoRender.objects.create(
                    folder_id=Folder.objects.get(id=folder_name),
                    profile_id=profile,
                    name_video = ''.join(random.choices(string.ascii_letters + string.digits, k=7)),
                    url_video_youtube=[],
                    text_content=content,
                    is_render_start = True,

                    title=title,
                    description=description,
                    keywords=keyword,
                    time_upload=time_upload,
                    date_upload=date_formatted,
                    status_video= "Render",
                    intro_active = profile.channel_intro_active,
                    intro_url = profile.channel_intro_url,
                    outro_active = profile.channel_outro_active,
                    outro_url = profile.channel_outro_url,
                    logo_active = profile.channel_logo_active,
                    logo_url = profile.channel_logo_url,
                    logo_position = profile.channel_logo_position,
                    font_text = font_text.font_name,

                    font_size = profile.channel_font_size,
                    font_bold = profile.channel_font_bold,
                    font_italic = profile.channel_font_italic,
                    font_underline = profile.channel_font_underline,
                    font_strikeout = profile.channel_font_strikeout,

                    font_color = profile.channel_font_color,
                    font_color_opacity = profile.channel_font_color_opacity,
                    font_color_troke = profile.channel_font_color_troke,
                    font_color_troke_opacity = profile.channel_font_color_troke_opacity,

                    stroke_text = profile.channel_stroke_text,
                    font_background = profile.channel_font_background,
                    channel_font_background_opacity = profile.channel_font_background_opacity,

                    voice = profile.channel_voice,
                    voice_style = profile.channel_voice_style,
                    voice_speed = profile.channel_voice_speed,
                    voice_pitch = profile.channel_voice_pitch,
                    voice_volume = profile.channel_voice_volume
                )
                if video.title != 'Đang chờ cập nhật' and video.title != '' and not request.user.is_superuser:
                    Count_Use_data.objects.create(
                        use = request.user,
                        videoRender_id = video,
                        edit_thumnail = False,
                        edit_title = True,
                        creade_video = False,
                        title = title,
                        url_thumnail = video.url_thumbnail
                    )
                if thumnail:
                    filename = thumnail.name.strip()
                    filename = filename.replace(" ", "_")
                    file_name = default_storage.save(f"data/{video.id}/thumnail/{filename}", thumnail)
                    file_url = default_storage.url(file_name)
                    video.url_thumbnail = file_url

                    if not request.user.is_superuser :
                        Count_Use_data.objects.create(
                        use = request.user,
                        videoRender_id = video,
                        edit_thumnail = True,
                        edit_title = False,
                        creade_video = False,
                        title = title,
                        url_thumnail = video.url_thumbnail
                        )
                return JsonResponse({'success': True, 'id': video.id})
            else:
                return JsonResponse({'success': True,'id': video_id})

        elif action == "get-image-video":
            channel_name = request.POST.get('id-video-render')
            directories, files = default_storage.listdir(f"data/{channel_name}/image/")
            images = []
            for file in files:
                text = file
                if len(text) > 14:
                    text = text[:6] + '...' + text[-8:]
                    
                images.append({'url': default_storage.url(f"data/{channel_name}/image/{file}"), 'name': text})


            image_html = render_to_string('render/input-image.html', {'images': images})

            return JsonResponse({'success': True, 'image_html': image_html})

        elif action == 'add-image-video':
            channel_name = request.POST.get('id-video-render')
            profile = VideoRender.objects.get(id=channel_name)
            image = request.FILES.get('file')
            if image:
                filename = image.name.strip().replace(" ", "_")
                file_image = default_storage.save(f"data/{profile.id}/image/{filename}", image)
                file_url = default_storage.url(file_image)
                return JsonResponse({'success': True, 'url': file_url, 'name': filename})
            else:
                return JsonResponse({'success': False, 'error': 'No image provided'})
            
        elif action == 'delete-image-video':
            channel_name = request.POST.get('id-video-render')
            image = request.POST.get('image_url')
            file_name = self.get_filename_from_url(image)
            default_storage.delete(f"data/{channel_name}/image/{file_name}")
            return JsonResponse({'success': True, 'message': 'Xóa ảnh thành công!'})

        elif action == 'save-text-video':
            video_id = request.POST.get('id-video-edit')
            video = VideoRender.objects.get(id=video_id)
            input_title = request.POST.get('input-title')
            input_description = request.POST.get('input-description')
            input_keyword = request.POST.get('input-keyword')
            input_date_upload = request.POST.get('input-date-upload')
            input_time_upload = request.POST.get('input-time-upload')
            input_content = request.POST.get('text-content')
            thumnail = request.FILES.get('input-Thumnail')
            json_text = request.POST.get('json_text')

            date_upload_datetime = datetime.strptime(input_date_upload, '%Y-%m-%d')
            date_formatted = date_upload_datetime.strftime('%Y-%m-%d')
            if video is not None:
                if request.user.is_superuser:
                    video.title = input_title
                    video.description = input_description
                    video.keywords = input_keyword
                    video.time_upload= input_time_upload
                    video.date_upload = date_formatted
                    video.text_content = input_content
                    video.text_content_2 = json_text
                    thumnail = request.FILES.get('input-Thumnail')
                    if thumnail :
                        if video.url_thumbnail:
                            image = video.url_thumbnail
                            file_name = self.get_filename_from_url(image)
                            default_storage.delete(f"data/{video_id}/image/{file_name}")
                        filename = thumnail.name.strip().replace(" ", "_")
                        file_name = default_storage.save(f"data/{video_id}/thumnail/{filename}", thumnail)
                        file_url = default_storage.url(file_name)
                        video.url_thumbnail = file_url
                    video.save()
                   
                else:
                    is_edit_title = Count_Use_data.objects.filter(videoRender_id=video,creade_video=False,edit_title=True,edit_thumnail=False).first()
                    is_edit_thumnail = Count_Use_data.objects.filter(videoRender_id=video,creade_video=False,edit_title=False,edit_thumnail=True).first()

                    # Trường hợp cả hai trường edit_title và edit_thumnail đều đang được chỉnh sửa bởi người khác
                    if (is_edit_title and is_edit_thumnail and 
                        is_edit_title.use != request.user and 
                        is_edit_thumnail.use != request.user):
                        return JsonResponse({'success': False, 'message': 'Video đang được chỉnh sửa bởi người khác!'})
                    
                    # Trường hợp chỉ trường edit_title đang được chỉnh sửa bởi người khác
                    elif is_edit_title and is_edit_title.use != request.user and input_title != video.title and input_title != "" and input_title not in "Đang chờ cập nhật":
                        return JsonResponse({'success': False, 'message': 'Tiêu đề đang được chỉnh sửa bởi người khác!'})
                    
                        
                    # Trường hợp chỉ trường edit_thumnail đang được chỉnh sửa bởi người khác
                    elif is_edit_thumnail and is_edit_thumnail.use != request.user and thumnail:
                        return JsonResponse({'success': False, 'message': 'Ảnh thumnail đang được chỉnh sửa bởi người khác!'})

                    # Trường hợp cả hai trường edit_title và edit_thumnail đều đang được chỉnh sửa bởi người hiện tại
                    elif (is_edit_title and is_edit_thumnail and 
                        is_edit_title.use == request.user and 
                        is_edit_thumnail.use == request.user):
                        video.description = input_description
                        video.keywords = input_keyword
                        video.time_upload= input_time_upload
                        video.date_upload = date_formatted
                        video.text_content = input_content
                        if input_title != video.title and input_title != "" and input_title not in "Đang chờ cập nhật":
                            video.title = input_title
                            video.save()
                            is_edit_title.title = input_title
                            is_edit_title.save()

                        if thumnail:
                            if video.url_thumbnail:
                                image = video.url_thumbnail
                                file_name = self.get_filename_from_url(image)
                                default_storage.delete(f"data/{video_id}/image/{file_name}")
                            filename = thumnail.name.strip().replace(" ", "_")
                            file_name = default_storage.save(f"data/{video_id}/thumnail/{filename}", thumnail)
                            file_url = default_storage.url(file_name)
                            video.url_thumbnail = file_url
                            video.save()
                            is_edit_thumnail.url_thumnail = file_url
                            is_edit_thumnail.save()
                            
                    # Trường hợp chỉ trường edit_title đang được chỉnh sửa bởi người dùng hiện tại
                    elif is_edit_title and is_edit_title.use == request.user and input_title != video.title and input_title != "" and input_title not in "Đang chờ cập nhật":
                        video.description = input_description
                        video.keywords = input_keyword
                        video.time_upload= input_time_upload
                        video.date_upload = date_formatted
                        video.text_content = input_content
                        if input_title != video.title and input_title != "" and input_title not in "Đang chờ cập nhật":
                            video.title = input_title
                            video.save()
                            is_edit_title.title = input_title
                            is_edit_title.save()

                    # Trường hợp chỉ trường edit_thumnail đang được chỉnh sửa bởi người dùng hiện tại
                    elif is_edit_thumnail and is_edit_thumnail.use == request.user and thumnail:
                        video.description = input_description
                        video.keywords = input_keyword
                        video.time_upload= input_time_upload
                        video.date_upload = date_formatted
                        video.text_content = input_content
                        if thumnail:
                            if video.url_thumbnail:
                                image = video.url_thumbnail
                                file_name = self.get_filename_from_url(image)
                                default_storage.delete(f"data/{video_id}/image/{file_name}")
                            filename = thumnail.name.strip().replace(" ", "_")
                            file_name = default_storage.save(f"data/{video_id}/thumnail/{filename}", thumnail)
                            file_url = default_storage.url(file_name)
                            video.url_thumbnail = file_url
                            video.save()
                            is_edit_thumnail.url_thumnail = file_url
                            is_edit_thumnail.save()

                            

        
                    # Trường hợp chưa có ai chỉnh sửa
                    elif not is_edit_title or not is_edit_thumnail:
                        video.description = input_description
                        video.keywords = input_keyword
                        video.time_upload= input_time_upload
                        video.date_upload = date_formatted
                        video.text_content = input_content
                        if input_title != video.title and input_title != "" and input_title not in "Đang chờ cập nhật":
                            video.title= input_title
                            video.save()
                            data = Count_Use_data.objects.create(
                                use = request.user,
                                videoRender_id = video,
                                edit_thumnail = False,
                                edit_title = True,
                                creade_video = False,
                                title = input_title,
                                url_thumnail = video.url_thumbnail
                            )

                        if thumnail:
                            if video.url_thumbnail:
                                image = video.url_thumbnail
                                file_name = self.get_filename_from_url(image)
                                default_storage.delete(f"data/{video_id}/image/{file_name}")
                            filename = thumnail.name.strip().replace(" ", "_")
                            file_name = default_storage.save(f"data/{video_id}/thumnail/{filename}", thumnail)
                            file_url = default_storage.url(file_name)
                            video.url_thumbnail = file_url
                            video.save()
                            data = Count_Use_data.objects.create(
                                use = request.user,
                                videoRender_id = video,
                                edit_thumnail = True,
                                edit_title = False,
                                creade_video = False,
                                title = input_title,
                                url_thumnail = file_url
                            )

            return JsonResponse({'success': True, 'message': 'Cập nhật video thành công!'})                           
        
        elif action == 'delete-video':
            if not request.user.has_perm('render.delete_videorender'):
                return JsonResponse({'success': False, 'message': 'Bạn không có quyền xóa video này.'})
            video_id = request.POST.get('id')
            video = VideoRender.objects.get(id=video_id)
            try:
                if video.url_thumbnail:
                    image = video.url_thumbnail
                    file_name = self.get_filename_from_url(image)
                    default_storage.delete(f"data/{video.id}/thumnail/{file_name}")
                directories, files = default_storage.listdir(f"data/{video.id}/image/")
                for file in files:
                    default_storage.delete(f"data/{video.id}/image/{file}")
            except Exception as e:
                pass
            # Xóa video
            video.delete()
            return JsonResponse({'success': True, 'message': 'Xóa video thành công!'})
        
        elif action == 'render-video':
            video_id = request.POST.get('id_video')
            video = VideoRender.objects.get(id=video_id)      
            if 'Đang Render' in video.status_video:
                result = AsyncResult(video.task_id)
                result.revoke(terminate=True)
                video.status_video = 'Đã Dừng Render'
                video.task_id = ''
                video.save()
            
            elif 'Đang chờ render video!' in video.status_video:
                result = AsyncResult(video.task_id)
                result.revoke(terminate=True)
                video.status_video = 'Render'
                video.save()
            else:
                language = Voice_language.objects.get(id=video.voice)
                voice = syle_voice.objects.get(id=video.voice_style)
                list_url_image = []
                directory = f'data/{video.id}/image'
                # Liệt kê các thư mục và file trong thư mục chỉ định
                directories, files = default_storage.listdir(directory)
                for file in files:
                    list_url_image.append(default_storage.url(f"{directory}/{file}"))
                data = {
                    'video_id': video.id,
                    'name_video': video.name_video,
                    "images": list_url_image,
                    "text": video.text_content_2,
                    'language':language.name,
                    'voice_id':voice.id_style,
                    'color':self.convert_color_to_ass(video.font_color,video.font_color_opacity),
                    'color_backrought' : self.convert_color_to_ass(video.font_background,video.channel_font_background_opacity),
                    'color_border':self.convert_color_to_ass(video.font_color_troke,video.font_color_troke_opacity),
                    'stroke_text': video.stroke_text,
                    'font_name':video.font_text,
                    'font_size':video.font_size,
                    'api_voice_korea': Api_Voice_ttsmaker.objects.first().Api_Voice_ttsmaker
                }
                
                video.status_video = 'Đang chờ render video!'
                task = render_video.apply_async(args=[data])
                video.task_id = task.id
                video.save()
            return JsonResponse({'success': True})
        
        elif action == 'get-text-video':
            image = request.FILES.get('file')
            if image:
                try:
                    img = Image.open(BytesIO(image.read()))  # Đảm bảo đọc đúng tệp ảnh
                    text = self.get_text_from_image(img)
                    # Trả về kết quả OCR dưới dạng JSON response
                    return JsonResponse({'success': True, 'text': text})

                except Exception as e:
                    return JsonResponse({'success': False, 'message': str(e)}, status=500)

            return JsonResponse({'success': False, 'message': 'No file uploaded'}, status=200)

        elif action == 'update_text_video':
            id = request.POST.get('id')
            text = request.POST.get('text_video')

            # Check if id and text_video are provided
            if not id or not text:
                return JsonResponse({'error': 'id and text_video are required'}, status=400)

            # Split the text into lines and remove empty lines
            text_list = [line for line in text.split('\n') if line.strip()]
            json_text = []

            # Create JSON structure for each line
            for row, item in enumerate(text_list):
                data = {
                    "id": row + 1,
                    "text": item,
                    'url_video': '',
                }
                json_text.append(data)

            # Retrieve the video object and update its text content
            try:
                video = VideoRender.objects.get(id=id)
            except VideoRender.DoesNotExist:
                return JsonResponse({'error': 'Video not found'}, status=404)

    
            # Retrieve the current text content JSON if available
            text_content_json = video.text_content_2 or "[]"
            text_content = json.loads(text_content_json)  # Deserialize the JSON string
            # Update url_video from the existing content if available
            for row, item in enumerate(json_text):
                if row < len(text_content):
                    item['url_video'] = text_content[row].get('url_video', '')
            
            content = render_to_string('render/item-text.html', {'text_content': json_text})
            return JsonResponse({'success': True, 'content': content})
        
        elif action == 'random-image':
            id_video = request.POST.get('id_video')
            try:
                id_video = int(id_video)
            except (TypeError, ValueError):
                return JsonResponse({'success': False, 'message': 'ID video không hợp lệ'})

            cache_key = f'image_list_{id_video}'
            image_list = cache.get(cache_key)
            
            if image_list is None:
                try:   
                    directories, files = default_storage.listdir(f"data/{id_video}/image/")
                except Exception as e:
                    return JsonResponse({'success': False, 'message': 'Không có ảnh nào vui lòng tải thêm ảnh!'})
                
                if not files:
                    return JsonResponse({'success': False, 'message': 'Không có ảnh nào vui lòng tải thêm ảnh!'})

                image_list = [default_storage.url(f"data/{id_video}/image/{file}") for file in files]
                cache.set(cache_key, image_list, timeout=60*15)  # Cache trong 15 phút
            
            video_list = ['/static/assets/img/no-image-available.png']
            
            try:
                num_layers = int(request.POST.get('rowCount'))
                Calculate = int(request.POST.get('count_image')) / 100
            except (TypeError, ValueError):
                return JsonResponse({'success': False, 'message': 'Dữ liệu đầu vào không hợp lệ'})

            # Calculate the number of images and videos
            num_images = int(num_layers * Calculate) 
            num_videos = num_layers - num_images 

            selected_images = random.choices(image_list, k=num_images)
            selected_videos = random.choices(video_list, k=num_videos)

            layer_contents = selected_images + selected_videos
            random.shuffle(layer_contents)

            return JsonResponse({'success': True, 'layer_contents': layer_contents})
        
    def get_text_from_image(self, image):
        data = Api_Key_Azure.objects.first()
        if data is None:
            return "Chưa cấu hình API Key!"

        subscription_key = data.subscription_key
        endpoint = data.endpoint
        
        try:
            computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))
        except Exception as e:
            return f"Lỗi khi khởi tạo ComputerVisionClient: {e}"

        with BytesIO() as output:
            try:
                image.save(output, format=image.format)
                output.seek(0)
            except Exception as e:
                return f"Lỗi khi lưu trữ hình ảnh: {e}"
            
            try:
                read_response = computervision_client.read_in_stream(output, raw=True)
            except Exception as e:
                return f"Lỗi khi gọi API đọc hình ảnh: {e}"
        
        try:
            operation_location = read_response.headers["Operation-Location"]
            operation_id = operation_location.split("/")[-1]
        except Exception as e:
            return f"Lỗi khi lấy Operation-Location từ response: {e}"

        while True:
            try:
                result = computervision_client.get_read_result(operation_id)
            except Exception as e:
                return f"Lỗi khi lấy kết quả đọc từ API: {e}"
            
            if result.status not in ['notStarted', 'running']:
                break
            time.sleep(1)
        
        if result.status == OperationStatusCodes.succeeded:
            text = ""
            for text_result in result.analyze_result.read_results:
                for line in text_result.lines:
                    text += line.text + "\n"
            return text
        else:
            return f"Lỗi: Kết quả API trả về với trạng thái {result.status}"

    def convert_color_to_ass(self,color_hex, opacity):
        # Chuyển đổi mã màu HEX sang RGB
        r = int(color_hex[1:3], 16)
        g = int(color_hex[3:5], 16)
        b = int(color_hex[5:7], 16)
        
        # Tính giá trị Alpha từ độ trong suốt
        alpha = round(255 * (1 - opacity / 100))
        
        # Định dạng lại thành mã màu ASS
        ass_color = f"&H{alpha:02X}{b:02X}{g:02X}{r:02X}&"
        
        return ass_color

@login_required(login_url="/login/")
def get_video_render(request):
    profile_id =  ProfileChannel.objects.get(id=request.GET.get('profile_id', None))
    chace_video_render = VideoRender.objects.filter(profile_id_id=profile_id.id)
    page = request.GET.get('page', 1)
    paginator = Paginator(chace_video_render, per_page=50)
    page_obj = paginator.get_page(page)

    video = render_to_string('render/video_show.html', {'page_obj': page_obj},request)
    page_obj = render_to_string('render/page_bar_template.html', {'page_obj': page_obj},request)
    info  = render_to_string('render/info.html', {'profile': profile_id})

    current_time = timezone.now().strftime('%Y-%m-%d')
    data = {
            'page_bar_html': page_obj,
            'video_html': video,
            'info_html': info,
            'current_time': current_time,
            'channel_time_upload' : profile_id.channel_time_upload
        }
    return JsonResponse(data)
        
@login_required(login_url="/login/")
def edit_video(request):
    video_id = request.GET.get('video_id')
    url_thumbnail = '/static/assets/img/no-image-available.png'
    form = VideoForm()
    current_time = timezone.now().strftime('%Y-%m-%d')
    if video_id == 'none':
        initial_data = {
            'title': 'Đang chờ cập nhật',
            'description': '',
            'keyword': '',
            'date_upload': current_time,
            'time_upload': '',
            'content': ''
        }
        form = VideoForm(initial=initial_data)
    else:
        data = get_object_or_404(VideoRender, id=video_id)
        if data.url_thumbnail:
            url_thumbnail = data.url_thumbnail
        initial_data = {
            'title': data.title,
            'description': data.description,
            'keyword': data.keywords,
            'date_upload': data.date_upload,
            'time_upload': data.time_upload,
            'content': data.text_content
        }
        form = VideoForm(initial=initial_data)
      

    content = render_to_string('render/edit-video.html', {
        'form': form,
        'thumbnail': url_thumbnail,
        'id': video_id,
      }, request)
    return JsonResponse({'success': True, 'edit_html': content})

def count_video_today(request):
    chace_count_use_data = get_count_use_data_from_cache()
    current_date = timezone.now().date()
    cread_video = len([f for f in chace_count_use_data if f['creade_video'] == True and f['use_id'] == request.user.id and f['timenow'] == current_date]) 
    edit_thumnail =  len([f for f in chace_count_use_data if f['edit_thumnail'] == True and f['use_id'] == request.user.id and f['timenow'] == current_date])
    edit_title = len([f for f in chace_count_use_data if f['edit_title'] == True and f['use_id'] == request.user.id and f['timenow'] == current_date])
    
    context = {
        'success': True,
        'text': f'<span class="text-primary">{current_date}</span> ---- VIDEO: <span class="text-danger">{cread_video}</span> ---- Tiêu ĐỀ: <span class="text-danger">{edit_title}</span> ---- Thumnail: <span class="text-danger">{edit_thumnail}</span>'
    }
    return JsonResponse(context)

class get_text_video(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    template_name = 'render/get-text-video.html'
    def get(self, request):
        return render(request, self.template_name)
    
class count_data(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    template_name = 'render/count_data_use.html'
    def get(self, request):
        all_users = CustomUser.objects.all()
        chace_count_use_data = get_count_use_data_from_cache()
        current_date = timezone.now().date()
        date = current_date.strftime("%Y-%m-%d")
        data = []
        current_date_old = date
        current_date_new = date
        
        for iteam in all_users:
            if not iteam.is_superuser:
                cread_video = len([f for f in chace_count_use_data if f['creade_video'] == True and f['use_id'] == iteam.id and f['timenow'] == current_date])
                edit_thumnail = len([f for f in chace_count_use_data if f['edit_thumnail'] == True and f['use_id'] == iteam.id and f['timenow'] == current_date])
                edit_title = len([f for f in chace_count_use_data if f['edit_title'] == True and f['use_id'] == iteam.id and f['timenow'] == current_date])
                
                data.append({
                    'user': iteam,
                    'cread_video': cread_video,
                    'edit_thumnail': edit_thumnail,
                    'edit_title': edit_title,
                })

        show_data = render_to_string('render/show_count.html', {'data': data}, request)

        return render(request, self.template_name, {'data': show_data, 'current_date_old': current_date_old, 'current_date_new': current_date_new})

    def post(self, request):
        action = request.POST.get('action')
        all_users = CustomUser.objects.all()
        chace_count_use_data = get_count_use_data_from_cache()
        chace_video_render = get_video_render_data_from_cache()
        
        if action == 'Seach':
            date_upload_old = request.POST.get('date_upload_old')
            date_upload_new = request.POST.get('date_upload_new')
            date_1 = datetime.strptime(date_upload_old, "%Y-%m-%d").date()
            date_2 = datetime.strptime(date_upload_new, "%Y-%m-%d").date()
            data = []
            for iteam in all_users:
                if not iteam.is_superuser:
                    cread_video = len([f for f in chace_count_use_data 
                                       if f['creade_video'] == True and 
                                       f['use_id'] == iteam.id and 
                                       date_1 <= f['timenow'] <= date_2])
                    
                    edit_thumnail = len([f for f in chace_count_use_data 
                                         if f['edit_thumnail'] == True and 
                                         f['use_id'] == iteam.id and 
                                         date_1 <= f['timenow'] <= date_2])
                    
                    edit_title = len([f for f in chace_count_use_data 
                                      if f['edit_title'] == True and 
                                      f['use_id'] == iteam.id and 
                                      date_1 <= f['timenow'] <= date_2])
                    
                    data.append({
                        'user': iteam,
                        'cread_video': cread_video,
                        'edit_thumnail': edit_thumnail,
                        'edit_title': edit_title,
                    })
            
            show_data = render_to_string('render/show_count.html', {'data': data}, request)
            
            return render(request, self.template_name, {'data': show_data, 'current_date_old': date_upload_old, 'current_date_new': date_upload_new})
        
        elif action == 'Date-Yesterday':
            current_date = timezone.now().date()

            # Lấy ngày hôm qua
            yesterday = current_date - timedelta(days=1)
            
            # Định dạng ngày hôm qua
            date_upload_old = yesterday.strftime("%Y-%m-%d")
            date_upload_new = yesterday.strftime("%Y-%m-%d")

            data = []

            for item in all_users:
                if not item.is_superuser:
                    cread_video = len([f for f in chace_count_use_data 
                                    if f['creade_video'] == True and 
                                    f['use_id'] == item.id and 
                                    yesterday <= f['timenow'] <= yesterday])
                    
                    edit_thumnail = len([f for f in chace_count_use_data 
                                        if f['edit_thumnail'] == True and 
                                        f['use_id'] == item.id and 
                                        yesterday <= f['timenow'] <= yesterday])
                    
                    edit_title = len([f for f in chace_count_use_data 
                                    if f['edit_title'] == True and 
                                    f['use_id'] == item.id and 
                                    yesterday <= f['timenow'] <= yesterday])
                    
                    data.append({
                        'user': item,
                        'cread_video': cread_video,
                        'edit_thumnail': edit_thumnail,
                        'edit_title': edit_title,
                    })
            
            show_data = render_to_string('render/show_count.html', {'data': data}, request)
            
            return render(request, self.template_name, {'data': show_data, 'current_date_old': date_upload_old, 'current_date_new': date_upload_new})

        elif action == 'Date-Today':
            current_date = timezone.now().date()
            date_1 = current_date
            date_2 = current_date

            date_old = current_date.strftime("%Y-%m-%d")
            date_new = current_date.strftime("%Y-%m-%d")
            
            data = []
            
            for iteam in all_users:
                if not iteam.is_superuser:
                    cread_video = len([f for f in chace_count_use_data 
                                       if f['creade_video'] == True and 
                                       f['use_id'] == iteam.id and 
                                       date_1 <= f['timenow'] <= date_2])
                    
                    edit_thumnail = len([f for f in chace_count_use_data 
                                         if f['edit_thumnail'] == True and 
                                         f['use_id'] == iteam.id and 
                                         date_1 <= f['timenow'] <= date_2])
                    
                    edit_title = len([f for f in chace_count_use_data 
                                      if f['edit_title'] == True and 
                                      f['use_id'] == iteam.id and 
                                      date_1 <= f['timenow'] <= date_2])
                    
                    data.append({
                        'user': iteam,
                        'cread_video': cread_video,
                        'edit_thumnail': edit_thumnail,
                        'edit_title': edit_title,
                    })
            
            show_data = render_to_string('render/show_count.html', {'data': data}, request)
            
            return render(request, self.template_name, {'data': show_data, 'current_date_old': date_old, 'current_date_new': date_new})
        
        elif action == 'Date-Month':
            date_upload_old = request.POST.get('date_upload_old')
            date_upload_new = request.POST.get('date_upload_new')
            
            date_1 = datetime.strptime(date_upload_old, "%Y-%m-%d").date()
            date_2 = datetime.strptime(date_upload_new, "%Y-%m-%d").date()

            # Get the first day of the month
            first_day_of_month = date_1.replace(day=1)
            
            # Get the last day of the month
            last_day_of_month = timezone.now().date()


            date_old = first_day_of_month.strftime("%Y-%m-%d")
            date_new = last_day_of_month.strftime("%Y-%m-%d")

            data = []
            
            for iteam in all_users:
                if not iteam.is_superuser:
                    cread_video = len([f for f in chace_count_use_data 
                                       if f['creade_video'] == True and 
                                       f['use_id'] == iteam.id and 
                                       first_day_of_month <= f['timenow'] <= last_day_of_month])
                    
                    edit_thumnail = len([f for f in chace_count_use_data 
                                         if f['edit_thumnail'] == True and 
                                         f['use_id'] == iteam.id and 
                                         first_day_of_month <= f['timenow'] <= last_day_of_month])
                    
                    edit_title = len([f for f in chace_count_use_data 
                                      if f['edit_title'] == True and 
                                      f['use_id'] == iteam.id and 
                                      first_day_of_month <= f['timenow'] <= last_day_of_month])
                    
                    data.append({
                        'user': iteam,
                        'cread_video': cread_video,
                        'edit_thumnail': edit_thumnail,
                        'edit_title': edit_title,
                    })
            
            show_data = render_to_string('render/show_count.html', {'data': data}, request)
            return render(request, self.template_name, {'data': show_data, 'current_date_old': date_old, 'current_date_new': date_new})
        
        elif action == 'show-thumnail':
            id = request.POST.get('id')
            page = request.POST.get('page')
            date_upload_old = request.POST.get('current_date_old')
            date_upload_new = request.POST.get('current_date_new')
            date_1 = datetime.strptime(date_upload_old, "%Y-%m-%d").date()
            date_2 = datetime.strptime(date_upload_new, "%Y-%m-%d").date()
            data = self.get_object(all_users,chace_count_use_data,chace_video_render,date_1,date_2,id)
            paginator = Paginator(data,9)
            page_obj = paginator.get_page(page)
            thumnail = render_to_string('render/show-image.html', {'page_obj': page_obj}, request)
            page_obj = render_to_string('render/thumnail_page_bar_template.html', {'page_obj': page_obj}, request)

            return JsonResponse({'success': True, 'thumnail_html': thumnail, 'page_bar_html': page_obj})
            
        elif action == 'show-title':
            id = request.POST.get('id')
            page = request.POST.get('page')
            date_upload_old = request.POST.get('current_date_old')
            date_upload_new = request.POST.get('current_date_new')
            date_1 = datetime.strptime(date_upload_old, "%Y-%m-%d").date()
            date_2 = datetime.strptime(date_upload_new, "%Y-%m-%d").date()
            data = self.get_tittel(all_users,chace_count_use_data,chace_video_render,date_1,date_2,id)
            paginator = Paginator(data,10)
            page_obj = paginator.get_page(page)
            title = render_to_string('render/show-titel.html', {'page_obj': page_obj}, request)
            page_obj = render_to_string('render/tittel_page_bar_template.html', {'page_obj': page_obj}, request)

            return JsonResponse({'success': True, 'title_html': title, 'page_bar_html': page_obj})

    def get_tittel(self,all_users,chace_count_use_data,chace_video_render,date_1,date_2,id):
        list_thumnail = []
        for iteam in all_users:
            if iteam.id == int(id):
                thumnail = [f for f in chace_count_use_data if f['edit_title'] == True and f['use_id'] == iteam.id and date_1 <= f['timenow'] <= date_2]
                for data in thumnail:
                    target_data = next((item for item in chace_video_render if item['id'] == data['videoRender_id_id']), None)
                    list_thumnail.append(target_data)
        return list_thumnail
    
    def get_object(self,all_users,chace_count_use_data,chace_video_render,date_1,date_2,id):
            list_thumnail = []
            for iteam in all_users:
                if iteam.id == int(id):
                    thumnail = [f for f in chace_count_use_data if f['edit_thumnail'] == True and f['use_id'] == iteam.id and date_1 <= f['timenow'] <= date_2]
                    for data in thumnail:
                        target_data = next((item for item in chace_video_render if item['id'] == data['videoRender_id_id']), None)
                        list_thumnail.append(target_data)
            return list_thumnail