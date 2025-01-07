import os
import requests
import socket

def get_public_ip():
    try:
        # Sử dụng ipify API để lấy địa chỉ IPv4 public
        response = requests.get("https://api.ipify.org")
        if response.status_code == 200:
            return response.text.strip()
        else:
            print(f"Failed to get public IP: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error getting public IP: {e}")
        return None

def get_local_ip():
   try:
       # Lấy hostname
       hostname = socket.gethostname()
       # Lấy địa chỉ IP local
       local_ip = socket.gethostbyname(hostname)
       return local_ip
   except Exception as e:
       print(f"Error getting local IP: {e}")
       return None

if __name__ == "__main__":
    # Lấy địa chỉ IP public
    # Lấy địa chỉ IP public
    public_ip = get_public_ip()
    local_ip = get_local_ip()
    print(f"dải ip của máy {public_ip} và {local_ip}")
    if public_ip == "210.245.74.61":
        # Nếu IP public trùng khớp, sử dụng IP local
        local_ip = get_local_ip()
        if local_ip:
            # Chạy Celery worker với IP local
            os.system(f"celery -A celeryworker worker -l INFO --hostname={local_ip}-Reup --concurrency=5 -Q render_video_content,render_video_reupload --prefetch-multiplier=1")
    else:
        os.system(f"celery -A celeryworker worker -l INFO --hostname={public_ip}-Reup --concurrency=3 -Q render_video_content,render_video_reupload --prefetch-multiplier=1")