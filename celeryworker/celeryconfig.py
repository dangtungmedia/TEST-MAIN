import os
from dotenv import load_dotenv

from channels.layers import get_channel_layer
from channels_redis.core import RedisChannelLayer


# Nạp biến môi trường từ file .env
load_dotenv()

# broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')

# # Kết quả backend
# result_backend =  os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')


# # Các cấu hình khác
# task_serializer = 'json'
# result_serializer = 'json'
# accept_content = ['json']
# timezone = 'UTC'


broker_url  =  os.environ.get('CELERY_BROKER_URL', 'redis://127.0.0.1:6379/0' )
result_backend  = os.environ.get('CELERY_RESULT_BACKEND', 'redis://127.0.0.1:6379/0')

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_CACHE', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [os.environ.get('REDIS_URL', 'redis://localhost:6379')],  # Fallback to local Redis
        },
    },
}

accept_content  = ['json']
task_serializer  = 'json'
result_serializer  = 'json'
timezone  = 'UTC'


broker_connection_retry_on_startup = True
