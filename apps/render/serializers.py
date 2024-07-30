from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import VideoRender
from apps.home.models import Voice_language, syle_voice,Folder,ProfileChannel
from django.core.files.storage import default_storage



class VoicelanguageSerializer(ModelSerializer):
    class Meta:
        model = Voice_language
        fields = '__all__'

class StyleVoiceSerializer(ModelSerializer):
    class Meta:
        model = syle_voice
        fields = ['id_style']

class FolderSerializer(ModelSerializer):
    class Meta:
        model = Folder
        fields = ['id','folder_name']

class RenderSerializer(ModelSerializer):
    class Meta:
        model = VideoRender
        fields = '__all__'


    

# class RenderSerializer(ModelSerializer):
    # voice_details = SerializerMethodField()
    # style = SerializerMethodField()

    # class Meta: 
    #     model = VideoRender
        # fields = ['voice_details', 'style', 'video_name','status_video','url_thumbnail','url_video','time_upload','date_upload']
        # fields = ['video_name','status_video','url_thumbnail','url_video','time_upload','date_upload']
        
    # def get_voice_details(self, obj):
    #     try:
    #         voice_detail = Voice_language.objects.get(id=obj.voice)
    #         return VoicelanguageSerializer(voice_detail).data
    #     except Voice_language.DoesNotExist:
    #         return None
    
    # def get_style(self, obj):
    #     try:
    #         style = syle_voice.objects.get(id=obj.voice_style)
    #         return StyleVoiceSerializer(style).data
    #     except syle_voice.DoesNotExist:
    #         return None
