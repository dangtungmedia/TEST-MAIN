from django.urls import path,re_path
from .consumers import RenderConsumer

websocket_urlpatterns = [
    # re_path(r"ws/update/", RenderConsumer.as_asgi()),
    path("ws/update_status/", RenderConsumer.as_asgi()),
]