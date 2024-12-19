import boto3

# Khởi tạo client
s3 = boto3.client(
    's3',
    endpoint_url='https://s3.autospamnews.com',
    aws_access_key_id='G4N6S01MHz180UGALp9f',
    aws_secret_access_key='RdTLoLOSQgI7EoqHemoddMFGS2ZxzH5hFIh0puO9'
)

# Kiểm tra kết nối
try:
    response = s3.list_buckets()
    print("Kết nối thành công!")
    print("Buckets:", response['Buckets'])
    
    # Upload file
    bucket_name = 'data'
    file_path = 'requirements.txt'  # Thay đổi đường dẫn file
    object_name = 'tung-media/file_của_bạn.txt'     # Tên file trên S3/MinIO
    
    # Cách 1: Sử dụng upload_file
    s3.upload_file(file_path, bucket_name, object_name)
    print(f"Upload thành công file {file_path} lên {bucket_name}/{object_name}")
    

except Exception as e:
    print("Lỗi:", str(e))
    