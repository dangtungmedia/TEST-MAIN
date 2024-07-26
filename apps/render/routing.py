from django.urls import path
from .consumers import RenderConsumer, CountDataConsumer

websocket_urlpatterns = [
    path('ws/update_status/<str:room_name>/', RenderConsumer.as_asgi()),
    path('ws/update_count/<str:room_name>/', CountDataConsumer.as_asgi()),
]
