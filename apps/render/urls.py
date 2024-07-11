from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

from apps.render import views
from .views import index, get_text_video, count_data

router = DefaultRouter()
router.register('render-video', views.VideoRenderViewSet, basename='render-video')  

app_name = 'render'

urlpatterns = [
    path('', include(router.urls)),
    path('render/', index.as_view(), name='home'),
    path('render/get-list-video/', views.get_video_render, name='get_video_render'),
    path('render/edit-video/', views.edit_video, name='edit-video'),
    path('render/count-data/', views.count_video_today, name='count-data'),
    path('render/get-text-video/', get_text_video.as_view(), name='get_text_video'),
    path('render/count-data-use/', count_data.as_view(), name='count_data_use'),
]