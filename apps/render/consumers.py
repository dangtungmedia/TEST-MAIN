from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import sync_to_async, async_to_sync
from .models import VideoRender
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer

@receiver(post_save, sender=VideoRender)
def notify_video_change(sender, instance, **kwargs):
    # Lấy layer kênh
    channel_layer = get_channel_layer()
    room_name = instance.profile_id.id
    room_group_name = f"render_profile_{room_name}"
    
    # Gửi thông báo đến group
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
        self.room_group_name = f"render_profile_{self.room_name}"

        # Thêm kênh vào group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        
    async def disconnect(self, close_code):
        # Loại bỏ kênh khỏi group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    @sync_to_async
    def get_video_data(self):
        videos = VideoRender.objects.filter(profile_id=self.room_name).values()
        data = [
            {
                'id': video['id'],
                'title': video['title'],
                'status': video['status_video'],
                'url_thumbnail': video['url_thumbnail'] if video['url_thumbnail'] else "/static/assets/img/no-image-available.png",
                'time_upload': video['time_upload'],
                'date_upload': video['date_upload'],
            } for video in videos
        ]
        return data

    async def video_change(self, event):
        try:
            data = await self.get_video_data()
            await self.send(text_data=json.dumps(data))
        except Exception as e:
            await self.send(text_data=json.dumps({"error": "An error occurred when processing video change event!"}))

    async def receive(self, text_data):
        # Xử lý thông điệp nhận được từ WebSocket
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        print(f"Received message: {message}")
