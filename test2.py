
import requests

url = "https://cdn.pixabay.com/video/2023/08/02/174358-851138337_small.mp4"
file_name = "video.mp4"

# Gửi yêu cầu GET để tải video
response = requests.get(url, stream=True)

# Kiểm tra trạng thái của yêu cầu
if response.status_code == 200:
    # Mở file và ghi dữ liệu video vào
    with open(file_name, "wb") as file:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)
    print(f"Video đã được tải về thành công với tên {file_name}")
else:
    print("Có lỗi xảy ra khi tải video.")