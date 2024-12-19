import boto3
import os
import sys
import threading

class ProgressPercentage(object):
    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(f'\rĐang upload {self._filename}: {percentage:.1f}%')
            sys.stdout.flush()

# Khởi tạo client
s3 = boto3.client(
    's3',
    endpoint_url='https://apis3.clouds3stonger.com',
    aws_access_key_id='G4N6S01MHz180UGALp9f',
    aws_secret_access_key='RdTLoLOSQgI7EoqHemoddMFGS2ZxzH5hFIh0puO9'
)
try:
    # Kiểm tra kết nối
    response = s3.list_buckets()
    print("Kết nối thành công!")
    
    # Thông tin upload
    bucket_name = 'tung-media'
    file_path = 'addxx.mp4'
    object_name = f'data/14327/{file_path}'
    
    # Upload file với progress callback
    print(f"\nBắt đầu upload file {file_path}...")
    
    s3.upload_file(
        file_path, 
        bucket_name, 
        object_name,
        Callback=ProgressPercentage(file_path),
        ExtraArgs={
            'ContentType': 'video/mp4',
            'ContentDisposition': 'inline'  # Để xem video trực tiếp
        }
    )
    
    # Tạo URL xem video
    url = s3.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': bucket_name,
            'Key': object_name,
            'ResponseContentType': 'video/mp4',
            'ResponseContentDisposition': 'inline'
        },
        ExpiresIn=365*24*60*60  # URL có hiệu lực 1 năm
    )
    
    print(f"\nUpload thành công!")
    print(f"URL xem video: {url}")

except FileNotFoundError:
    print(f"\nLỗi: Không tìm thấy file {file_path}")
except Exception as e:
    print(f"\nLỗi: {str(e)}")