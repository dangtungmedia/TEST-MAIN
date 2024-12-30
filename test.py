import websocket
import json
# print("xxxxxxxxxxxxxxx")
# # Kết nối WebSocket
# ws = websocket.WebSocket()
# ws.connect(f"wss://autospamnews.com/ws/update_status/")
# data = {
#     'type':'update-status',
#     'video_id': 9161,
#     'status': "Đang chờ render : Đợi đến lượt render",
#     'task_id': "none",
#     'worker_id': '',
#     'url_video': '',
# }
# # Kiểm tra trạng thái kết nối
# if ws.connected:
#     print("WebSocket connection established successfully!")

#     # Gửi tin nhắn tới server
#     message = {"action": "update_status", "data": "Hello, server!"}
#     ws.send(json.dumps(data))
#     print(f"Message sent: {message}")
# else:
#     print("WebSocket connection failed.")

from time import sleep

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
            return False
            
    def send(self, data, max_retries=5):
        for attempt in range(max_retries):
            try:
                if not self.ws or not self.ws.connected:
                    if not self.connect():
                        continue
                        
                self.ws.send(json.dumps(data))
                return True
            except Exception as e:
                sleep(1)  # Delay before retry
                continue
        return False

# Khởi tạo WebSocket client một lần
ws_client = WebSocketClient("wss://autospamnews.com/ws/update_status/")

data = {
    'type':'update-status',
    'video_id': 9161,
    'status': "Đang chờ render : Đợi đến lượt render",
    'task_id': "none",
    'worker_id': '',
    'url_video': '',
}

ws_client.send(data)