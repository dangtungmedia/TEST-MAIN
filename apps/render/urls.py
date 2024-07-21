from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

from apps.render import views
from .views import index,VideoRenderViewSet,ProfileChannelViewSet,VideoRenderList

router = DefaultRouter()
router.register('profiles',ProfileChannelViewSet,basename='profiles')
router.register('render-video', VideoRenderViewSet, basename='render-video')  

app_name = 'video_render'
urlpatterns = [
    path('', include(router.urls)),
    path('render/', index.as_view(), name='render'),
    path('count-data/', VideoRenderList.as_view(), name='count-data'),
]