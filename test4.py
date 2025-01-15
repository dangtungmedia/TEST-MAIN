import os
import random
import json
import requests
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import Set, List, Dict
import logging
from urllib.parse import urlparse
from requests.adapters import HTTPAdapter  
from requests.packages.urllib3.util.retry import Retry
import logging
import sys

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('download.log', encoding='utf-8'),  # File log hỗ trợ Unicode
        logging.StreamHandler(sys.stdout)  # Console hỗ trợ Unicode
    ]
)

class VideoDownloader:
    def __init__(self, json_file: str, output_dir: str, max_videos: int = 10000):
        self.json_file = Path(json_file)
        self.output_dir = Path(output_dir)
        self.max_videos = max_videos
        self.selected_urls: Set[str] = set()
        self.downloaded_count = 0  # Biến đếm video đã tải thành công
        
        # Headers giả lập trình duyệt
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'video/webm,video/mp4,video/*;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://pixabay.com/'
        }
        
        # Cấu hình retry
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        
        # Tạo thư mục output nếu chưa tồn tại
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def load_urls(self) -> List[Dict]:
        """Load và xáo trộn URLs từ file JSON"""
        with open(self.json_file, 'r') as file:
            data = json.load(file)
        return random.sample(data, len(data))

    def is_file_downloaded(self, url: str) -> bool:
        """Kiểm tra xem video đã tồn tại trong thư mục hay chưa"""
        file_name = os.path.basename(urlparse(url).path)
        return (self.output_dir / file_name).exists()

    def download_single_video(self, item: Dict, index: int, max_retries: int = 10) -> bool:
        """Tải một video đơn lẻ"""
        url = item['url']
        file_name = os.path.basename(urlparse(url).path)
        file_path = self.output_dir / file_name

        # Bỏ qua nếu file đã tồn tại
        if file_path.exists():
            logging.info(f"[{index}] Video đã tồn tại: {file_name}, bỏ qua.")
            return True
        
        for attempt in range(1, max_retries + 1):
            try:
                time.sleep(2)  # Delay giữa các request
                logging.info(f"[{index}] Đang tải: {file_name} (Thử lần {attempt})")
                response = self.session.get(url, headers=self.headers, stream=True, timeout=30)
                response.raise_for_status()

                file_size = 0
                with open(file_path, 'wb') as video_file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            video_file.write(chunk)
                            file_size += len(chunk)

                if file_size > 0:
                    self.downloaded_count += 1  # Tăng biến đếm
                    logging.info(f"[{index}] Tải thành công: {file_name} ({file_size/1024/1024:.2f}MB)")
                    logging.info(f"Đã tải {self.downloaded_count}/{self.max_videos} video.")
                    return True
                else:
                    logging.warning(f"[{index}] File rỗng: {file_name}")
                    file_path.unlink(missing_ok=True)
                    return False

            except requests.exceptions.RequestException as e:
                logging.error(f"[{index}] Lỗi khi tải video (Lần {attempt}): {file_name} - {str(e)}")
                if attempt == max_retries:
                    logging.warning(f"[{index}] Đổi URL sau {max_retries} lần thử.")
        return False

    def download_videos(self, max_workers: int = 4):
        """Tải nhiều video đồng thời"""
        all_urls = self.load_urls()
        index = 1

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            
            while self.downloaded_count < self.max_videos and all_urls:
                item = all_urls.pop()
                if item['url'] in self.selected_urls or self.is_file_downloaded(item['url']):
                    continue  # Bỏ qua nếu URL đã tải hoặc file đã tồn tại

                future = executor.submit(self.download_single_video, item, index)
                futures.append((future, item['url'], index))
                index += 1

            for future, url, idx in futures:
                if future.result():
                    self.selected_urls.add(url)

        logging.info(f"Tải thành công {self.downloaded_count} video vào thư mục '{self.output_dir}'")

if __name__ == "__main__":
    downloader = VideoDownloader(
        json_file='filtered_data.json',
        output_dir='video',
        max_videos=10000
    )
    downloader.download_videos(max_workers=40)

