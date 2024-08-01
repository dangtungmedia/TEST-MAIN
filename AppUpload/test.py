import os
import requests
import shutil
from requests.exceptions import RequestException
from urllib3.exceptions import ProtocolError

class FileDownloader:
    def download_file(self, url, directory, filename, retries=3):
        attempt = 0
        while attempt < retries:
            try:
                response = requests.get(url, stream=True)
                if response.status_code == 200:
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                    path = os.path.join(directory, filename)
                    with open(path, 'wb') as file:
                        response.raw.decode_content = True
                        shutil.copyfileobj(response.raw, file)
                    return True
                else:
                    print(f"Failed to download file: {response.status_code}")
                    return False
            except (RequestException, ProtocolError) as e:
                attempt += 1
                print(f"Attempt {attempt} failed: {e}")
                if attempt < retries:
                    print("Retrying...")
        print("Failed to download the file after multiple attempts")
        return False

# Sử dụng hàm download_file
url_video = "https://s3-hcm5-r1.longvan.net/19425936-media/data/234/thumnail/OIP.jpg?AWSAccessKeyId=AUQESQVFF01YMVGUPVF9&Signature=9cWEBoVNZD3%2BGDMTasvUVEN8EqU%3D&Expires=4400273089"
directory = "Video_Upload"
filename = "video.png"

downloader = FileDownloader()
success = downloader.download_file(url_video, directory, filename)

if success:
    print("File downloaded successfully")
else:
    print("Failed to download file")
