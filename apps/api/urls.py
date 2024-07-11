from django.urls import path,re_path
from django.conf.urls.static import static

from apps.api.views import ApiApp



app_name = 'render'

urlpatterns = [
    path('api/<int:id>/',ApiApp.as_view(), name='api_app'),
]
    
