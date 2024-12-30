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
    ip_address = get_public_ip()
    if ip_address:
        # Chạy Celery worker với số lượng worker tính được
        os.system(f"celery -A celeryworker worker -l INFO --hostname=Tung-Content --concurrency=2 -Q render_video_content")
    else:
        print("Không thể lấy địa chỉ IP public.")
