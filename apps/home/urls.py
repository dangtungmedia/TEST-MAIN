# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path,re_path
from apps.home import views
from django.conf import settings
from django.conf.urls.static import static
from .views import setting,Index



app_name = 'home'

urlpatterns = [
    path('', Index.as_view(), name='home'),
    path('setting/', setting.as_view(), name='setting'),
    path('load-channel/', views.load_channel, name='load-channel'),
    path('load-channel-setting/', views.load_channel_setting, name='load-channel-setting'),
    path('load-style-voice/', views.load_styler_voice, name='load-style-voice')
]
