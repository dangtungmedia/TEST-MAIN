from rest_framework import serializers
from .models import *


class ProfileChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileChannel
        fields = '__all__'