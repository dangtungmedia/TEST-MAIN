print("xxxxxxxxxxx")

import requests

# URL của API
url = "https://iloveyt.net/proxy.php"

# Dữ liệu form gửi tới server
form = {
    "url": "https://www.youtube.com/watch?v=xRfHOwpFwHc"
}

# Gửi POST request
response = requests.post(url, data=form)

# Chuyển đổi phản hồi sang JSON
data = response.json()


title = data["api"]["title"]
mediaPreviewUrl = data["api"]["previewUrl"]
mediaThumbnail = data["api"]["imagePreviewUrl"]

# In ra kết quả
print(title)
print(mediaPreviewUrl)
print(mediaThumbnail)


# Tên file bạn muốn lưu
output_file = "video.mp4"

# Gửi yêu cầu GET để tải video
response = requests.get(mediaPreviewUrl)

# Tên file muốn lưu
output_file = "video.mp4"

# Gửi yêu cầu GET với stream=True
response = requests.get(mediaPreviewUrl, stream=True)

# Kiểm tra trạng thái phản hồi
if response.status_code == 200:
    total_size = int(response.headers.get('content-length', 0))  # Tổng kích thước file
    downloaded_size = 0  # Kích thước đã tải
    with open(output_file, "wb") as file:
        for chunk in response.iter_content(chunk_size=1024):  # Tải từng chunk
            if chunk:  # Nếu chunk không rỗng
                file.write(chunk)
                downloaded_size += len(chunk)
                percent_done = (downloaded_size / total_size) * 100
                print(f"Đã tải: {percent_done:.2f}%", end="\r")
    print(f"\nVideo đã được tải thành công và lưu tại {output_file}.")
else:
    print(f"Lỗi khi tải video: {response.status_code}")