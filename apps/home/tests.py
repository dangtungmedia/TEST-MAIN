from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from .forms import ProfileChannelForm
from .models import Folder, ProfileChannel, Font_Text, Voice_language, syle_voice
from django.contrib.auth.decorators import login_required
from django.template import loader
from django.urls import reverse
from apps.home.serializers import ProfileChannelSerializer
from django.core.files.storage import default_storage
import random
import string
from urllib.parse import urlparse, unquote
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.login.models import CustomUser
from apps.login.forms import LoginInfor, ChangePasswordForm
from django.contrib.auth import update_session_auth_hash

from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
import requests

from  apps.render.models import VideoRender,DataTextVideo,video_url,Count_Use_data
import os
class Index(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    template_name = 'home/User-profile.html'
    
    def get(self, request):
        user = CustomUser.objects.get(id=request.user.id)
        form = LoginInfor(initial={
            'email': user.email,
            'full_name': user.full_name,
            'name_bank': user.name_bank,
            'bank_number': user.bank_number,
            'phone_number': user.phone_number
        })
        form_2 = ChangePasswordForm(request.user)
        return render(request, self.template_name,{"form":form ,"form_2":form_2})
        
    def post(self, request):
        success = None
        msg = None
        form = LoginInfor(request.POST)
        form_2 = ChangePasswordForm(request.user)  # Truyền user vào form_2 khi khởi tạo
        action = request.POST.get('action')

        if action == 'update-infor':
            if form.is_valid():
                try:
                    user = CustomUser.objects.get(id=request.user.id)
                    user.email = form.cleaned_data['email']
                    user.full_name = form.cleaned_data['full_name']
                    user.name_bank = form.cleaned_data['name_bank']
                    user.bank_number = form.cleaned_data['bank_number']
                    user.phone_number = form.cleaned_data['phone_number']
                    user.save()
                    msg = 'Cập Nhập Thông Tin Thành Công'
                    success = True
                except:
                    msg = 'Cập Nhập Thông Tin Thất Bại'
                    success = False

        elif action == 'change-password':
            form_2 = ChangePasswordForm(request.user, request.POST) 
            if form_2.is_valid():
                form_2.save()
                update_session_auth_hash(request, form_2.user)  # Important!
                msg = 'Đổi Mật Khẩu Thành Công'
                success = True
            else:
                msg = 'Đổi Mật Khẩu Thất Bại '
                success = False
        return render(request, self.template_name,{"form": form ,"form_2": form_2,"msg": msg, "success": success})

class setting(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    template_name = 'home/setting.html'

    def set_form_choices(self, request ,form, profiles, profile):
        form.fields['channel_name'].queryset = profiles
        form.fields['channel_name_setting'].queryset = profiles


        form.fields['folder_name'].queryset = Folder.objects.all()
        form.fields['folder_name_seting'].queryset = Folder.objects.all()
        form.fields['forder_setting'].queryset = Folder.objects.all()
        form.fields['channel_forder_name_setting'].queryset = Folder.objects.all()

        if profile is None:
            voice = syle_voice.objects.filter(voice_language=1)
        else:
            voice = syle_voice.objects.filter(voice_language=profile.channel_voice)

        choices = [(voice.id_style, voice.style_name) for voice in voice]
        form.fields['channel_voice_style'].choices = choices



        

    def get(self, request):
        folder = Folder.objects.first()
        profiles = ProfileChannel.objects.filter(folder_name=folder)
        voices = Voice_language.objects.all()
        profile = profiles.first()
        data = self.show_channel(folder,profile)
        form = ProfileChannelForm(initial=data)
        self.set_form_choices(request,form, profiles, profile)
        fonts = self.list_fonts()
        
        return render(request, self.template_name, {'form': form, 'fonts': fonts ,'voices': voices})

    def show_channel(self,folder,profile):
        if profile is None:
            initial_data = {
                'folder_name': folder,
                'channel_name': profile,
                'channel_forder_setting':folder,
                'channel_forder_name_setting': folder,
                'channel_name_setting':profile,

                'input_folder_name': '',
                'input_channel_name': '',

                'channel_intro_active': False,
                'channel_intro_url': '',

                'channel_outro_active': False,
                'channel_outro_url': '',

                'channel_logo_active': False,
                'channel_logo_url': '',

                'channel_logo_position': 'left',
                
                'channel_font_text': 1,
                'channel_font_text_setting': 1,

                'channel_font_size': 40,

                'channel_font_bold' : False,
                'channel_font_italic': False,
                'channel_font_underline': False,
                'channel_font_strikeout': False,


                'channel_font_color': '#FFFFFF',
                'channel_font_color_opacity': 100,

                'channel_font_color_troke':'#000000',
                'channel_font_color_troke_opacity': 100,


                'channel_font_background' : '#008CFF',
                'channel_font_background_opacity': 0,

                'channel_stroke_text': 1,
                'channel_subtitle_text' : 'Đây là phần subtittel của kênh',
                
                'channel_voice': 1,
                'channel_voice_setting': 1,
                'channel_voice_style' : 6,

                'channel_voice_speed' : 50,
                'channel_voice_pitch' : 50,
                'channel_voice_volume' : 50,

                'channel_text_voice': '',

                'channel_title': '',
                'channel_description': '',
                'channel_keywords': '',
                'channel_time_upload': '',
                'channel_url': '',
                'channel_email_login': '',
                'channel_vps_upload':'',
            }
        else:
            initial_data = {
                'folder_name': folder,
                'channel_name': profile,
                'channel_forder_setting':folder,
                'channel_forder_name_setting': folder,
                'channel_name_setting':profile,

                'input_folder_name': '',
                'input_channel_name': '',

                'channel_intro_active': profile.channel_intro_active,
                'channel_intro_url': profile.channel_intro_url,

                'channel_outro_active': profile.channel_outro_active,
                'channel_outro_url': profile.channel_outro_url,

                'channel_logo_active': profile.channel_logo_active,
                'channel_logo_url': profile.channel_logo_url,

                'channel_logo_position': profile.channel_logo_position,
                
                'channel_font_text': profile.channel_font_text,
                'channel_font_text_setting': profile.channel_font_text,

                'channel_font_size': profile.channel_font_size,

                'channel_font_bold' : profile.channel_font_bold,
                'channel_font_italic': profile.channel_font_italic,
                'channel_font_underline': profile.channel_font_underline,
                'channel_font_strikeout': profile.channel_font_strikeout,


                'channel_font_color': profile.channel_font_color,
                'channel_font_color_opacity': profile.channel_font_color_opacity,

                'channel_font_color_troke': profile.channel_font_color_troke,
                'channel_font_color_troke_opacity': profile.channel_font_color_troke_opacity,


                'channel_font_background' : profile.channel_font_background,
                'channel_font_background_opacity': profile.channel_font_background_opacity,

                'channel_stroke_text': profile.channel_stroke_text,
                'channel_subtitle_text' : profile.channel_font_subtitle,
                
                'channel_voice': profile.channel_voice,
                'channel_voice_setting': profile.channel_voice,
                'channel_voice_style' : profile.channel_voice_style,

                'channel_voice_speed' : profile.channel_voice_speed,
                'channel_voice_pitch' : profile.channel_voice_pitch,
                'channel_voice_volume' : profile.channel_voice_volume,

                'channel_text_voice': profile.channel_text_voice,
                'channel_title': profile.channel_title,
                'channel_description': profile.channel_description,
                'channel_keywords': profile.channel_keywords,
                'channel_time_upload': profile.channel_time_upload,
                'channel_url': profile.channel_url,
                'channel_email_login': profile.channel_email_login,
                'channel_vps_upload': profile.channel_vps_upload,
            }
        return initial_data

    def get_filename_from_url(self,url):
        # Phân tích URL
        parsed_url = urlparse(url)
        # Lấy đường dẫn và giải mã phần trăm encoding
        path = unquote(parsed_url.path)
        # Lấy tên file từ phần cuối của đường dẫn
        filename = path.split('/')[-1]
        return filename

    def post(self, request):
        form = ProfileChannelForm(request.POST, request.FILES)
        action = request.POST.get('action')        
        channel_voice = request.POST.get('channel_voice')

        # Xử lý trường channel_voice_style
        voice = syle_voice.objects.filter(voice_language=channel_voice)
        choices = [(v.id_style, v.style_name) for v in voice]
        form.fields['channel_voice_style'].choices = choices

        # Xử lý trường channel_name và channel_name_setting
        folder_name = request.POST.get('folder_name')
        channel_folder_name_setting = request.POST.get('channel_forder_name_setting')

        if folder_name != '':
            form.fields['channel_name'].queryset = ProfileChannel.objects.filter(folder_name=folder_name)
        else:
            form.fields['channel_name'].queryset = ProfileChannel.objects.none()

        if channel_folder_name_setting != '':
            form.fields['channel_name_setting'].queryset = ProfileChannel.objects.filter(folder_name=channel_folder_name_setting)
        else:
            form.fields['channel_name_setting'].queryset = ProfileChannel.objects.none()

        form.fields['folder_name'].queryset = Folder.objects.all()
        form.fields['folder_name_seting'].queryset = Folder.objects.all()
        form.fields['forder_setting'].queryset = Folder.objects.all()
        form.fields['channel_forder_name_setting'].queryset = Folder.objects.all()
        success = None
        msg = None  

        if action == 'get-infor-setting':
            channel_name = request.POST.get('channel_name')
            if channel_name != '':
                folder_id = request.POST.get('folder_name')
                channel_id = request.POST.get('channel_name')
                folder = Folder.objects.get(id=folder_id)
                profiles = ProfileChannel.objects.filter(folder_name=folder)
                profile = ProfileChannel.objects.get(id=channel_id)
                data = self.show_channel(folder,profile)
                form = ProfileChannelForm(initial=data)
                self.set_form_choices(request,form, profiles, profile)
                return render(request, self.template_name, {'form': form})
            else:
                folder_name = request.POST.get('folder_name')
                if  folder_name != '':
                    profiles = ProfileChannel.objects.filter(folder_name=folder_name)
                    profile = None
                    data = self.show_channel(folder_name,profile)
                    form = ProfileChannelForm(initial=data)
                    self.set_form_choices(request,form, profiles, profile)
                    return render(request, self.template_name, {'form': form})
                
        if form.is_valid():
            if  action =='folder-add':
                folder_name = request.POST.get('input_folder_name')
                if folder_name:
                    try:
                        folder = Folder.objects.create(folder_name=folder_name, use=request.user)
                        success = True
                        msg = 'Thêm Thư Mục Thành Công'
                        profiles = ProfileChannel.objects.filter(folder_name=folder)
                        profile = profiles.first()
                        data = self.show_channel(folder,profile)
                        form = ProfileChannelForm(initial=data)
                        self.set_form_choices(request,form, profiles, profile)
                    except Exception as e:
                        success = False
                        msg = 'Thêm Thư Mục Thất Bại , Tên Thư Mục Đã Tồn Tại'
                    return render(request, self.template_name, {'form': form ,'success': success,'msg': msg})
                
            if action == 'folder-delete':
                folder_id = request.POST.get('forder_setting')
                if folder_id:
                    ProfileChannel.objects.filter(folder_name=folder_id).delete()
                    Folder.objects.filter(id=folder_id).delete()
                    success = True
                    msg = 'Xóa Thư Mục Thành Công'
                    if folder_id == request.POST.get('folder_name'):
                        folder = Folder.objects.first()
                        profiles = ProfileChannel.objects.filter(folder_name=folder)
                        profile = profiles.first()
                        data = self.show_channel(folder,profile)
                        form = ProfileChannelForm(initial=data)
                        self.set_form_choices(request,form, profiles, profile)
                        return render(request, self.template_name, {'form': form ,'success': success,'msg': msg})
                    else:
                        return render(request, self.template_name, {'form': form ,'success': success,'msg': msg})
                else:
                    success = False
                    msg = 'Xóa Thư Mục Thất Bại'
                    return render(request, self.template_name, {'form': form ,'success': success,'msg': msg})
            
            if action == 'folder-update':
                folder_id = request.POST.get('forder_setting')
                folder_name = request.POST.get('input_folder_name')
                if folder_id and folder_name:
                    Folder.objects.filter(id=folder_id).update(folder_name=folder_name)
                    folder = Folder.objects.get(id=folder_id)  # get the updated Folder instance
                    success = True
                    msg = 'Cập Nhập Thư Mục Thành Công'
                    profiles = ProfileChannel.objects.filter(folder_name=folder)
                    channel = request.POST.get('channel_name')
                    try:
                        profile = ProfileChannel.objects.get(id=channel)
                    except:
                        profile = profiles.first()
                    data = self.show_channel(folder,profile)
                    form = ProfileChannelForm(initial=data)
                    self.set_form_choices(request,form, profiles, profile)
                else:
                    success = False
                    msg = 'Cập Nhập Thư Mục Thất Bại'
                return render(request, self.template_name, {'form': form ,'success': success,'msg': msg})
            

            
            if action == 'add-channel':
                input_channel_name = request.POST.get('input_channel_name')
                channel_folder_name_setting = request.POST.get('channel_forder_name_setting')

                if channel_folder_name_setting and input_channel_name:
                    try:
                        folder_name = Folder.objects.get(id=channel_folder_name_setting)
                    except Folder.DoesNotExist:
                        folder_name = None

                    if folder_name:
                        if not ProfileChannel.objects.filter(folder_name=folder_name, channel_name=input_channel_name).exists():
                            font  = Font_Text.objects.first()
                            profile = ProfileChannel.objects.create(folder_name=folder_name, channel_name=input_channel_name, channel_font_text=font)
                            success = True
                            msg = 'Thêm profile Thành Công'

                            profiles = ProfileChannel.objects.filter(folder_name=folder_name)
                            data = self.show_channel(folder_name, profile)
                            form = ProfileChannelForm(initial=data)
                            self.set_form_choices(request,form, profiles, profile)
                        else:
                            success = False
                            msg = 'Thêm profile Thất Bại, Tên Profile Đã Tồn Tại'
                    else:
                        success = False
                        msg = 'Thư Mục Không Tồn Tại'
                else:
                    success = False
                    msg = 'Thêm Kênh Thất Bại'

                return render(request, self.template_name, {'form': form, 'success': success, 'msg': msg})

            if action == 'delete-channel':
                channel_id = request.POST.get('channel_name_setting')

                if channel_id:
                    try:
                        profile = ProfileChannel.objects.get(id=channel_id)
                        profile.delete()
                        success = True
                        msg = 'Xóa Kênh Thành Công'
                    except ProfileChannel.DoesNotExist:
                        success = False
                        msg = 'Kênh không tồn tại hoặc đã bị xóa trước đó'
                else:
                    success = False
                    msg = 'Vui Lòng Chọn Profile Để Xóa'

                return render(request, self.template_name, {'form': form, 'success': success, 'msg': msg})

            if action == "update-channel":
                channel_id = request.POST.get('channel_name_setting')
                channel_name = request.POST.get('input_channel_name')

                if channel_id and channel_name:
                    try:
                        ProfileChannel.objects.filter(id=channel_id).update(channel_name=channel_name)
                        success = True
                        msg = 'Cập Nhập Kênh Thành Công'
                    except ProfileChannel.DoesNotExist:
                        success = False
                        msg = 'Kênh không tồn tại hoặc đã bị xóa trước đó'
                else:
                    success = False
                    msg = 'Cập Nhập Kênh Thất Bại'

                return render(request, self.template_name, {'form': form, 'success': success, 'msg': msg})
            
            if action == 'logo-setting':
                channel_name = request.POST.get('channel_name')
                if channel_name != '':
                    try:
                        data = ProfileChannel.objects.get(id=channel_name)
                        data.channel_logo_position = form.cleaned_data['channel_logo_position']
                        data.save()
                        success = True
                        msg = 'Cập Nhập Logo Thành Công'
                    except ProfileChannel.DoesNotExist:
                        success = False
                        msg = 'Kênh không tồn tại hoặc đã bị xóa trước đó'
                else:
                    success = False
                    msg = 'Cập Nhập Logo Thất Bại'

                return render(request, self.template_name, {'form': form, 'success': success, 'msg': msg})

            if action == 'save-fontext':  
                channel_name = request.POST.get('channel_name')
                if channel_name != '':
                    try:
                        data = ProfileChannel.objects.get(id=channel_name)
                        data.channel_font_text = form.cleaned_data['channel_font_text_setting']
                        data.channel_font_size = form.cleaned_data['channel_font_size']
                        data.channel_font_bold = form.cleaned_data['channel_font_bold']
                        data.channel_font_italic = form.cleaned_data['channel_font_italic']
                        data.channel_font_underline = form.cleaned_data['channel_font_underline']
                        data.channel_font_strikeout = form.cleaned_data['channel_font_strikeout']
                        data.channel_font_color = form.cleaned_data['channel_font_color']
                        data.channel_font_color_opacity = form.cleaned_data['channel_font_color_opacity']
                        data.channel_font_color_troke = form.cleaned_data['channel_font_color_troke']
                        data.channel_font_color_troke_opacity = form.cleaned_data['channel_font_color_troke_opacity']
                        data.channel_font_background = form.cleaned_data['channel_font_background']
                        data.channel_font_background_opacity = form.cleaned_data['channel_font_background_opacity']
                        data.channel_stroke_text = form.cleaned_data['channel_stroke_text']
                        data.channel_font_subtitle = form.cleaned_data['channel_subtitle_text']
                        data.save()
                        success = True
                        msg = 'Cập Nhập Font Text Thành Công'
                    except ProfileChannel.DoesNotExist:
                        success = False
                        msg = 'Kênh không Cập Nhập Font Text Thất Bại'
                else:
                    success = False
                    msg = 'Kênh không tồn tại hoặc đã bị xóa trước đó'
                return render(request, self.template_name, {'form': form, 'success': success, 'msg': msg})
        
            if action == 'save-voice':
                channel_name = request.POST.get('channel_name')
                if channel_name != '':
                    try:
                        data = ProfileChannel.objects.get(id=channel_name)
                        data.channel_voice = request.POST.get('channel_voice')
                        data.channel_voice_style = request.POST.get('channel_voice_style')
                        data.channel_voice_speed = form.cleaned_data['channel_voice_speed']
                        data.channel_voice_pitch = form.cleaned_data['channel_voice_pitch']
                        data.channel_voice_volume = form.cleaned_data['channel_voice_volume']
                        data.channel_text_voice = form.cleaned_data['channel_text_voice']
                        data.save()
                        success = True

                        msg = 'Cập Nhập Voice Thành Công'
                    except ProfileChannel.DoesNotExist:
                        success = False
                        msg = 'Cập Nhập Voice Thất Bại'

                else:
                    success = False
                    msg = 'Kênh không tồn tại hoặc đã bị xóa trước đó'
                return render(request, self.template_name, {'form': form, 'success': success, 'msg': msg})
        
            if action == 'save-channel':
                channel_name = request.POST.get('channel_name')
                if channel_name != '':
                    try:
                        data = ProfileChannel.objects.get(id=channel_name)

                        intro_file = request.FILES.get('channel_intro_input_file')
                        outro_file = request.FILES.get('channel_outro_input_file')
                        logo_file = request.FILES.get('channel_logo_input_file')

                        if intro_file:
                            if data.channel_intro_url:
                                old_filename = self.get_filename_from_url(data.channel_intro_url)
                                default_storage.delete(f"profile/{data.id}/intro/{old_filename}")

                            filename = intro_file.name.strip()
                            filename = filename.replace(" ", "_")
                            file_name = default_storage.save(f"profile/{data.id}/intro/{filename}", intro_file)
                            file_url = default_storage.url(file_name)
                            data.channel_intro_url = file_url

                        if outro_file:
                            if data.channel_outro_url:
                                old_filename = self.get_filename_from_url(data.channel_outro_url)
                                default_storage.delete(f"profile/{data.id}/outro/{old_filename}")

                            filename = outro_file.name.strip()
                            filename = filename.replace(" ", "_")
                            file_name = default_storage.save(f"profile/{data.id}/outro/{filename}", outro_file)
                            file_url = default_storage.url(file_name)
                            data.channel_outro_url = file_url

                        if logo_file:
                            if data.channel_logo_url:
                                old_filename = self.get_filename_from_url(data.channel_logo_url)
                                default_storage.delete(f"profile/{data.id}/logo/{old_filename}")

                            filename = logo_file.name.strip()
                            filename = filename.replace(" ", "_")
                            file_name = default_storage.save(f"profile/{data.id}/logo/{filename}", logo_file)
                            file_url = default_storage.url(file_name)
                            data.channel_logo_url = file_url

                        data.channel_intro_active = form.cleaned_data['channel_intro_active']
                        data.channel_outro_active = form.cleaned_data['channel_outro_active']
                        data.channel_logo_active = form.cleaned_data['channel_logo_active']
                        

                        data.channel_title = form.cleaned_data['channel_title']
                        data.channel_description = form.cleaned_data['channel_description']
                        data.channel_keywords = form.cleaned_data['channel_keywords']
                        data.channel_time_upload = form.cleaned_data['channel_time_upload']
                        data.channel_url = form.cleaned_data['channel_url']
                        data.channel_email_login = form.cleaned_data['channel_email_login']
                        data.channel_vps_upload = form.cleaned_data['channel_vps_upload']
                        
                        data.save()
                        success = True
                        msg = 'Cập Nhập Channel Thành Công'

                        folder = Folder.objects.get(id=data.folder_name.id)
                        profiles = ProfileChannel.objects.filter(folder_name=folder)
                        profile = ProfileChannel.objects.get(id=channel_name)
                        data = self.show_channel(folder,profile)
                        form = ProfileChannelForm(initial=data)
                        self.set_form_choices(request,form, profiles, profile)
                        return render(request, self.template_name, {'form': form, 'success': success, 'msg': msg})
                    
                    except ProfileChannel.DoesNotExist:
                        success = False
                        msg = 'Cập Nhập Channel Thất Bại'
                        return render(request, self.template_name, {'form': form, 'success': success, 'msg': msg})
                else:
                    success = False
                    msg = 'Kênh không tồn tại hoặc đã bị xóa trước đó'
                    return render(request, self.template_name, {'form': form, 'success': success, 'msg': msg})
        else:
            success = False
            msg = 'Dữ Liệu Không Hợp Lệ'

        return render(request, self.template_name, {'form': form ,'success': success,'msg': msg})


    def list_fonts(self):
        fonts = []
        directory = "apps/static/assets/fonts"
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".ttf") or file.endswith(".otf"):
                    relative_path = os.path.relpath(os.path.join(root, file), directory)
                    parts = relative_path.split(os.sep)
                    font_name = parts[-1].replace('.ttf', '').replace('.otf', '')
                    font_entry = {
                        'name': f"{parts[-2]}-{font_name}",
                        'urlfont': os.path.join(root, file).replace("\\", "/")
                    }
                    fonts.append(font_entry)
        return fonts
           
@login_required(login_url="/login/")
def load_channel(request):
    folder_name = request.GET.get("folder_name")
    folder_name = Folder.objects.get(id=folder_name)
    channel_names = ProfileChannel.objects.filter(folder_name=folder_name)
    profile_html = render_to_string('home/load-channel.html', {'channel_names': channel_names})
    if channel_names.exists():
        data = {
            'profile_html': profile_html,
            'data': ProfileChannelSerializer(channel_names[0]).data,
        }
    else:
        data = {
            'profile_html': profile_html,
            'data': None,
        }
    return JsonResponse(data)

@login_required(login_url="/login/")
def load_channel_setting(request):
    folder_name = request.GET.get("channel_forder_setting")
    channel_names = ProfileChannel.objects.filter(folder_name=folder_name)
    return render(request, 'home/load-channel.html', {'channel_names': channel_names})

@login_required(login_url="/login/")    
def load_styler_voice(request):
    voice_id = request.GET.get("channel_voice")
    voice_id = Voice_language.objects.get(id=voice_id)
    voice = syle_voice.objects.filter(voice_language=voice_id)
    profile_html = render_to_string('home/load-style-voice.html', {'channel_voice': voice})
    data = {
            'voice_styler': profile_html,
        }
    return JsonResponse(data)