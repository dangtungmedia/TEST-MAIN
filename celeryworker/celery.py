from celery import Celery

# Tạo ứng dụng Celery với tên 'celeryworker'
app = Celery('celeryworker')

# Nạp cấu hình từ file 'celeryconfig.py' trong package 'celeryworker'
app.config_from_object('celeryworker.celeryconfig')

# Tự động tìm kiếm và nạp các task từ các module chỉ định trong package 'celeryworker'
app.autodiscover_tasks(['celeryworker'])

# Thiết lập timezone cho Celery
app.conf.timezone = 'Asia/Ho_Chi_Minh'  # Sử dụng đúng cú pháp với chữ hoa

# Các cấu hình khác
app.conf.worker_timeout = 120
#thời gian chờ giữa các lần kiểm tra worker
app.conf.worker_heartbeat_interval = 30
app.conf.broker_connection_retry_on_startup = True
app.conf.accept_content = ['json']
app.conf.task_serializer = 'json'
app.conf.result_serializer = 'json'

app.conf.task_acks_late = True  # Xác nhận task sau khi xử lý
app.conf.worker_prefetch_multiplier = 1  # Mỗi worker chỉ nhận 1 task

# Định nghĩa một task debug đơn giản
@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
