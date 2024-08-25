from django.contrib import admin

# Register your models here.
from .models import VideoRender, DataTextVideo,video_url,Count_Use_data,APIKeyGoogle,Api_Voice_ttsmaker
admin.site.register(VideoRender)
admin.site.register(DataTextVideo)
admin.site.register(video_url)
admin.site.register(Count_Use_data)
admin.site.register(APIKeyGoogle)
admin.site.register(Api_Voice_ttsmaker)
