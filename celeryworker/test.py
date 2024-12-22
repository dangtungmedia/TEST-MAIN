import websocket
import json
print("xxxxxxxxxxxxxxx")
# Kết nối WebSocket
ws = websocket.WebSocket()
ws.connect(f"wss://autospamnews.com/ws/update_status/")
data = {
    'type':'update-status',
    'video_id': video_id,
    'status': status_video,
    'task_id': task_id,
    'worker_id': worker_id,
    'url_video': url_video,
}
# Kiểm tra trạng thái kết nối
if ws.connected:
    print("WebSocket connection established successfully!")

    # Gửi tin nhắn tới server
    message = {"action": "update_status", "data": "Hello, server!"}
    ws.send(json.dumps(data))
    print(f"Message sent: {message}")

    # Nhận phản hồi từ server
    response = ws.recv()
    print(f"Response from server: {response}")

else:
    print("WebSocket connection failed.")