# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.test import TestCase

# Create your tests here.
from django.db import models

# Create your models here.

class Forlder(models.Model):
    name_forder = models.CharField(max_length=100)
    timenow = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 
    def __str__(self):
        return self.name_forder

class ProfileSetting(models.Model):

    profile_Channel_id = models.ForeignKey(Forlder, on_delete=models.CASCADE)

    name_profile = models.CharField(max_length=100)

    is_intro = models.BooleanField(default=False)
    url_intro = models.URLField(default='')

    is_outro = models.BooleanField(default=False)
    url_outro = models.URLField(default='')

    is_logo = models.BooleanField(default=False)
    url_logo = models.URLField(default='')


    logo_position = models.CharField(max_length=5, default='left', verbose_name="Vị trí Logo")


    text_subtitle = models.CharField(max_length=300)

    fonttext = models.CharField(max_length=100,blank=True, null=True)
    fontsize = models.CharField(max_length=100)



    font_isbold = models.BooleanField(default=False)
    font_isitalic = models.BooleanField(default=False)
    font_isunderline = models.BooleanField(default=False)
    font_isstrikeout = models.BooleanField(default=False)
    font_color = models.CharField(max_length=100)
    opacityfontcolor = models.CharField(max_length=100)
    fontcolorsize = models.CharField(max_length=100)
    opacityfontcolorsize = models.CharField(max_length=100)

    backgroundcolor = models.CharField(max_length=100)
    opacitybackgroundcolor = models.CharField(max_length=100)
    
    border_color = models.CharField(max_length=100)

    voice_language = models.CharField(max_length=100)

    id_voice_language = models.CharField(max_length=100)


    titelSetting = models.CharField(max_length=100)
    descriptionSetting = models.TextField()
    keywordSetting = models.CharField(max_length=100)
    email_profile_channel = models.EmailField(max_length=200)
    url_profile_channel = models.URLField(max_length=200)
    ip_vps_upload = models.CharField(max_length=200)
    time_upload_channel = models.CharField(max_length=200)
   
    
    
    

    voicespeed = models.CharField(max_length=100)
    voicevolume = models.CharField(max_length=100)
    voicepitch = models.CharField(max_length=100)
    voiceisbold = models.BooleanField(default=False)

    def __str__(self):
        return self.nameprofile
    

class Speaker(models.Model):
    name = models.CharField(max_length=100)
    speaker_uuid = models.CharField(max_length=100)
    def __str__(self):
        return self.name
    
class Style(models.Model):
    Speaker_id = models.ForeignKey(Speaker, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name