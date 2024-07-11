from rest_framework.serializers import ModelSerializer
from apps.render.models import VideoRender


class RenderSerializer(ModelSerializer):
    class Meta: 
        model = VideoRender
        fields = '__all__'
        