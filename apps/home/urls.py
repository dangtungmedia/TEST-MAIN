# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path,re_path
from django.urls import path, include
from django.conf.urls.static import static
from .views import SettingView,IndexView
from rest_framework.routers import DefaultRouter
from .views import FolderViewSet,ProfileViewSet,StyleVoiceViewSet
from django.conf import settings


app_name = 'home'

router = DefaultRouter()
router.register(r'folders', FolderViewSet, basename='folders')
router.register(r'profiles', ProfileViewSet, basename='profiles')
router.register(r'styler-voice', StyleVoiceViewSet, basename='styler-voice')


urlpatterns = [
    path('', IndexView.as_view(), name='home'),
    path('setting/', SettingView.as_view(), name='setting'),
    path('home/', include(router.urls)),  # Bao gồm router URLs dưới đường dẫn /api/
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)