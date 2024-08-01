# apps/home/serializers.py
from rest_framework import serializers
from .models import ProfileChannel, Folder, Font_Text, syle_voice, Voice_language



class VoiceLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voice_language
        fields = '__all__'

class StyleVoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = syle_voice
        fields = '__all__'


class FontTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = Font_Text
        fields =  '__all__'


        
class FolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = '__all__'

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileChannel
        fields = '__all__'
