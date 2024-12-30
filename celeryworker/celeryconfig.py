import os
from dotenv import load_dotenv

# Nạp biến môi trường từ file .env
load_dotenv()
broker_url  =  os.environ.get('CELERY_BROKER_URL', 'redis://127.0.0.1:6379/0' )
result_backend  = os.environ.get('CELERY_RESULT_BACKEND', 'redis://127.0.0.1:6379/0')

