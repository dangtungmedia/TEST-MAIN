import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async, async_to_sync
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from django.utils import timezone
from .models import VideoRender, Count_Use_data
from apps.home.models import ProfileChannel
from .serializers import RenderSerializer
from apps.login.models import CustomUser

# Đổi tên hàm notify_video_change để tránh xung đột
@receiver(post_save, sender=VideoRender)
def notify_video_render_change(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    room_name = instance.profile_id.id
    room_group_name = f"render_{room_name}"
    async_to_sync(channel_layer.group_send)(
        room_group_name,
        {
            'type': 'video_change',
            'message': 'update'
        }
    )

class RenderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"render_{self.room_name}"
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    @sync_to_async
    def get_video_data(self):
        profile = ProfileChannel.objects.get(id=int(self.room_name))
        videos = VideoRender.objects.filter(profile_id=profile)
        serializer = RenderSerializer(videos, many=True)
        return serializer.data

    async def video_change(self, event):
        try:
            data = await self.get_video_data()
            await self.send(text_data=json.dumps(data))
        except Exception as e:
            await self.send(text_data=json.dumps({"error": "An error occurred when processing video change event!"}))

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        print(f"Received message: {message}")
        data = await self.get_video_data()
        await self.send(text_data=json.dumps(data))

# Đổi tên hàm notify_video_change để tránh xung đột
@receiver(post_save, sender=Count_Use_data)
def notify_count_use_change(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    room_name = instance.profile_id.id
    room_group_name = f"USRER_{room_name}"
    async_to_sync(channel_layer.group_send)(
        room_group_name,
        {
            'type': 'video_change',
            'message': 'update'
        }
    )

class CountDataConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"USRER_{self.room_name}"
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    @sync_to_async
    def get_video_data(self):
        user = CustomUser.objects.get(id=int(self.room_name))
        current_date = timezone.now().date()

        if user.is_superuser:
            cread_video = Count_Use_data.objects.filter(creade_video=True, timenow=current_date).count()
            edit_title = Count_Use_data.objects.filter(edit_title=True, timenow=current_date).count()
            edit_thumnail = Count_Use_data.objects.filter(edit_thumnail=True, timenow=current_date).count()
            text = f'<span class="text-primary">{current_date}</span> ----Video: <span class="text-danger">{cread_video}</span> ---- Title: <span class="text-danger">{edit_title}</span> ---- Thumbnail: <span class="text-danger">{edit_thumnail}</span>'
        else:
            cread_video = Count_Use_data.objects.filter(use=user, creade_video=True, timenow=current_date).count()
            edit_title = Count_Use_data.objects.filter(use=user, edit_title=True, timenow=current_date).count()
            edit_thumnail = Count_Use_data.objects.filter(use=user, edit_thumnail=True, timenow=current_date).count()
            text = f'<span class="text-primary">{current_date}</span> ---- VIDEO: <span class="text-danger">{cread_video}</span> ---- Title: <span class="text-danger">{edit_title}</span> ---- Thumbnail: <span class="text-danger">{edit_thumnail}</span>'
        return text

    async def video_change(self, event):
        try:
            data = await self.get_video_data()
            await self.send(text_data=json.dumps({'message': data}))
        except Exception as e:
            await self.send(text_data=json.dumps({"error": "An error occurred when processing video change event!"}))

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        print(f"Received message: {message}")
        data = await self.get_video_data()
        await self.send(text_data=json.dumps({'message': data}))
