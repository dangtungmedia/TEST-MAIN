from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from .models import Folder, ProfileChannel, Font_Text, Voice_language, syle_voice
from django.contrib.auth.decorators import login_required
from django.template import loader
from django.urls import reverse
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

from rest_framework import viewsets
from .serializers import FolderSerializer, ProfileSerializer, StyleVoiceSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import ProfileChannel, Folder, Voice_language, Font_Text


from rest_framework.routers import DefaultRouter
from  .models import Folder, ProfileChannel
from rest_framework.permissions import IsAuthenticated


class FolderViewSet(viewsets.ModelViewSet):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None 


    @action(detail=False, methods=['post'], url_path='get-folders')
    def get_folders_by_user(self, request):
        is_content = request.data.get('is_content', None)
        user_id = request.data.get('userId', None)
        print(is_content)
        print(user_id)

        queryset = Folder.objects.all()
        for folder in queryset:
            print(folder.is_content)


        if is_content is None or user_id is None:
            return Response({"status": "error", "message": "Invalid parameters"}, status=400)

        if request.user.is_superuser:
            channels = self.queryset.filter(is_content=is_content)
            print(channels)
        else:
            channels = self.queryset.filter(user_id=user_id, is_content=is_content)

        serializer = self.get_serializer(channels, many=True)
        print(serializer.data)
        return Response({"status": "success", "folders": serializer.data})
    



class ProfileViewSet(viewsets.ModelViewSet):
    queryset = ProfileChannel.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None 

    @action(detail=False, methods=['get'], url_path='by-folder/(?P<folder_id>\d+)')
    def get_folders_by_user(self, request, folder_id=None):
        channels  = self.queryset.filter(folder_name_id=folder_id)
        serializer = self.get_serializer(channels, many=True)
        return Response(serializer.data)
    
class StyleVoiceViewSet(viewsets.ModelViewSet):
    queryset = syle_voice.objects.all()
    serializer_class = StyleVoiceSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None 

    @action(detail=False, methods=['get'], url_path='by-Voide/(?P<voice_language_id>\d+)')
    def get_folders_by_user(self, request, voice_language_id=None):
        channels = self.queryset.filter(voice_language_id=voice_language_id)
        serializer = self.get_serializer(channels, many=True)
        return Response(serializer.data)



class IndexView(LoginRequiredMixin, TemplateView):
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

class SettingView(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    template_name = 'home/setting.html'
    def get(self, request):
       # Lấy tất cả các thư mục có is_content=True
        content = True
        folders = Folder.objects.filter(is_content=content)
        
        # Lấy thư mục đầu tiên nếu có tồn tại
        folders_first = folders.first() if folders.exists() else None

        # Lấy tất cả profile liên quan đến thư mục đầu tiên
        profiles = ProfileChannel.objects.filter(folder_name_id=folders_first.id) if folders_first else []
        profiles_first = profiles.first() if profiles else None

        # Lấy tất cả các font, sắp xếp theo ngôn ngữ
        fonts = Font_Text.objects.all().order_by('font_language')

        # Lấy tất cả ngôn ngữ giọng nói
        folder_voice = Voice_language.objects.all()

        # Render trang với context đã chuẩn bị
        return render(request, self.template_name, {
            'content': content,
            "folders": folders,
            "profiles": profiles,
            "fonts": fonts,
            "folder_voice": folder_voice,
            "profilesFirst": profiles_first,
        })