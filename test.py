import requests

# URL của API
url = "https://iloveyt.net/proxy.php"

# Dữ liệu form gửi tới server
form = {
    "url": "https://www.youtube.com/watch?v=HF1syyQGNYw"
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
