from django.db import models
from apps.home.models import Folder, Font_Text, syle_voice, Voice_language, ProfileChannel
from apps.login.models import CustomUser
# Create your models here.

class VideoRender(models.Model):
    folder_id = models.ForeignKey(Folder, on_delete=models.CASCADE)
    profile_id = models.ForeignKey(ProfileChannel, on_delete=models.CASCADE)
    name_video = models.TextField(max_length=100, blank=True)
    url_video_youtube = models.TextField(max_length=100, blank=True)
    text_content = models.TextField(default="",blank=True)
    text_content_2 = models.TextField(default="",blank=True)
    task_id = models.CharField(max_length=255, blank=True, null=True)
    worker_id = models.CharField(max_length=255, null=True, blank=True)  # ID của worker
    status_video = models.TextField(default="Đang Chờ Cập Nhập Tiêu Đề & Thumnail",blank=True)
    is_render_start = models.BooleanField(default=False,blank=True)

    url_audio = models.TextField(default="",blank=True)
    url_subtitle = models.TextField(default="",blank=True)


    video_image = models.TextField(default="",blank=True)
    url_thumbnail = models.TextField(blank=True)
    url_video = models.TextField(blank=True)

    intro_active = models.BooleanField(default=False,blank=True)
    intro_url = models.TextField(blank=True,default='')
    outro_active = models.BooleanField(default=False,blank=True)
    outro_url = models.TextField(blank=True,default='')
    logo_active = models.BooleanField(default=False,blank=True)
    logo_url = models.TextField(blank=True,default='')
    logo_position = models.TextField(max_length=100, blank=True,default='left')

    font_text = models.TextField(default='',blank=True)
    font_size = models.IntegerField(default=30,blank=True)
    font_bold = models.BooleanField(default=False,blank=True)
    font_italic = models.BooleanField(default=False,blank=True)
    font_underline = models.BooleanField(default=False,blank=True)
    font_strikeout = models.BooleanField(default=False,blank=True)

    font_color = models.TextField(max_length=100, blank=True,default='#FFFFFF')
    font_color_opacity = models.IntegerField(default=100,blank=True)

    font_color_troke = models.TextField(max_length=100, blank=True,default='#000000')
    font_color_troke_opacity = models.IntegerField(default=0,blank=True)

    stroke_text = models.DecimalField(max_digits=10, decimal_places=2,default=1,blank=True)
    font_background = models.TextField(max_length=100, blank=True,default='#ffffff')
    channel_font_background_opacity = models.IntegerField(default=0,blank=True)

    voice = models.IntegerField(default=1, blank=True)
    voice_style = models.IntegerField(default=1,blank=True)
    voice_speed = models.IntegerField(default=50,blank=True)
    voice_pitch = models.IntegerField(default=50,blank=True)
    voice_volume = models.IntegerField(default=50,blank=True)
    text_voice = models.TextField(default="",blank=True)


    title = models.TextField(default="",blank=True)
    description = models.TextField(default="",blank=True)
    keywords = models.TextField(default="",blank=True)
    time_upload = models.TextField(default="",blank=True)
    date_upload = models.TextField(default="",blank=True)


    timenow = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name_video
    
class DataTextVideo(models.Model):
    folder_id = models.ForeignKey(Folder, on_delete=models.CASCADE, null=True)
    url_video = models.URLField(max_length=100)
    count_text = models.IntegerField()
    id_channel = models.URLField(max_length=100)
    title = models.CharField(max_length=200)
    text_video = models.TextField()
    timenow = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 
    def __str__(self):
        return self.url_video
    
class video_url(models.Model):
    folder_id  =  models.ForeignKey(Folder, on_delete=models.CASCADE, null=True)
    profile_id = models.ForeignKey(ProfileChannel, on_delete=models.CASCADE, null=True)
    url = models.URLField(max_length=200)
    timenow = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 
    def __str__(self):
        return self.url
    
class Count_Use_data(models.Model):
    use  =  models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    videoRender_id = models.ForeignKey(VideoRender, on_delete=models.SET_NULL, null=True)
    edit_thumnail = models.BooleanField(default=False)
    edit_title = models.BooleanField(default=False)
    creade_video = models.BooleanField(default=False)
    title = models.TextField(default="",blank=True)
    url_thumnail = models.TextField(default="",blank=True)
    timenow = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.use.username
    
class Api_Key_Azure(models.Model):
    subscription_key = models.TextField(default="",blank=True)
    endpoint = models.TextField(default="",blank=True)
    timenow = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.subscription_key

class Api_Voice_ttsmaker(models.Model):
    Api_Voice_ttsmaker = models.TextField(default="",blank=True)
    timenow = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.Api_Voice_ttsmaker