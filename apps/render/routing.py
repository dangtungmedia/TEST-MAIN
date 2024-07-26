from django.urls import path,re_path
from .consumers import RenderConsumer

websocket_urlpatterns = [
    re_path(r"ws/update_status/(?P<room_name>\w+)/$", RenderConsumer.as_asgi()),
]