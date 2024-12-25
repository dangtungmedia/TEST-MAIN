from celery import shared_task
import websocket
import json
from time import sleep
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

class WebSocketClient:
    def __init__(self, url):
        self.url = url
        self.ws = None
        
    def connect(self):
        try:
            if self.ws is None or not self.ws.connected:
                self.ws = websocket.WebSocket()
                self.ws.connect(self.url)
                return True
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
            return False
            
    def send(self, data, max_retries=3):
        for attempt in range(max_retries):
            try:
                if not self.ws or not self.ws.connected:
                    if not self.connect():
                        continue
                        
                self.ws.send(json.dumps(data))
                return True
            except Exception as e:
                logger.error(f"Send attempt {attempt + 1} failed: {e}")
                sleep(1)  # Delay before retry
                continue
        return False
    
 # Khởi tạo WebSocket client một lần
ws_client = WebSocketClient("wss://autospamnews.com/ws/update_status/")


@shared_task(
    bind=True, 
    priority=0,
    name='render_video',
    time_limit=14200,
    queue='render_video_content',
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3, 'countdown': 5}
)
def render_video(self, data):
    task_id = self.request.id
    worker_id = self.request.hostname
    video_id = data.get('video_id')
    
    if not video_id:
        logger.error("No video_id provided in data")
        return False
        
    logger.info(f"Starting render for video_id: {video_id}")
    
   
    
    try:
        for i in range(10000):
            status = update_status_video(
                ws_client,
                i,
                video_id,
                task_id,
                worker_id
            )
            if not status:
                logger.error(f"Failed to update status at iteration {i}")
                
    except Exception as e:
        logger.error(f"Error in render_video task: {e}")
        raise  # Let Celery retry
def update_status_video(ws_client, status_video, video_id, task_id, worker_id, url_video=None):
    data = {
        'type': 'update-status',
        'video_id': video_id,
        'status': status_video,
        'task_id': task_id,
        'worker_id': worker_id,
        'url_video': url_video,
    }
    
    return ws_client.send(data)