# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models

import string,random
from apps.login.models import CustomUser
# Create your models here.

class Folder(models.Model):
    use = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True)
    folder_name = models.CharField(max_length=100,blank=True,unique=True)
    def __str__(self):  
        return self.folder_name
    
class Font_Text(models.Model):
    font_name = models.CharField(max_length=100, blank=True)
    def __str__(self):  
        return self.font_name
    
class syle_voice(models.Model):
    id_style = models.IntegerField(default=0,blank=True)
    name_voice = models.CharField(max_length=100, blank=True)
    style_name = models.CharField(max_length=100, blank=True)
    voice_language = models.ForeignKey('Voice_language', on_delete=models.CASCADE, blank=True, null=True)
    def __str__(self):  
        return self.style_name
    
class Voice_language(models.Model):
    name = models.CharField(max_length=100, blank=True)
    speaker_uuid = models.CharField(max_length=100, blank=True)
    def __str__(self):  
        return self.name
    
class ProfileChannel(models.Model):
    folder_name = models.ForeignKey(Folder, on_delete=models.CASCADE, blank=True, null=True)
    channel_name = models.CharField(max_length=100, blank=True)
    channel_intro_active = models.BooleanField(default=False,blank=True)
    channel_intro_url = models.TextField(blank=True,default='')
    channel_outro_active = models.BooleanField(default=False,blank=True)
    channel_outro_url = models.TextField(blank=True,default='')
    channel_logo_active = models.BooleanField(default=False,blank=True)
    channel_logo_url = models.TextField(blank=True,default='')
    channel_logo_position = models.TextField(max_length=100, blank=True,default='left')

    channel_font_text = models.ForeignKey(Font_Text, on_delete=models.CASCADE, blank=True, null=True)
    channel_font_size = models.IntegerField(default=30,blank=True)
    channel_font_bold = models.BooleanField(default=False,blank=True)
    channel_font_italic = models.BooleanField(default=False,blank=True)
    channel_font_underline = models.BooleanField(default=False,blank=True)
    channel_font_strikeout = models.BooleanField(default=False,blank=True)

    channel_font_color = models.TextField(max_length=100, blank=True,default='#000000')
    channel_font_color_opacity = models.IntegerField(default=100,blank=True)

    channel_font_color_troke = models.TextField(max_length=100, blank=True,default='#000000')
    channel_font_color_troke_opacity = models.IntegerField(default=100,blank=True)

    channel_stroke_text = models.DecimalField(max_digits=10, decimal_places=1,default=1,blank=True)

    channel_font_background = models.TextField(max_length=100, blank=True,default='#ffffff')
    channel_font_background_opacity = models.IntegerField(default=0,blank=True)

    channel_font_subtitle = models.TextField(default="Đây là phần subtittel của kênh")

    channel_voice = models.IntegerField(default=1, blank=True)
    channel_voice_style = models.IntegerField(default=0,blank=True)
    channel_voice_speed = models.IntegerField(default=50,blank=True)
    channel_voice_pitch = models.IntegerField(default=50,blank=True)
    channel_voice_volume = models.IntegerField(default=50,blank=True)
    channel_text_voice = models.TextField(default="",blank=True)

    channel_title = models.TextField(default="",blank=True)
    channel_description = models.TextField(default="",blank=True)
    channel_keywords = models.TextField(default="",blank=True)

    channel_time_upload = models.TextField(default="",blank=True)
    channel_url = models.TextField(default="",blank=True)
    channel_email_login = models.TextField(default="",blank=True)
    channel_vps_upload = models.TextField(default="",blank=True)

    channel_money = models.DecimalField(max_digits=10, decimal_places=2,default=0,blank=True)
    channel_view_count = models.IntegerField(default=0,blank=True, null=True)
    
    def __str__(self):  
        return self.channel_name
   