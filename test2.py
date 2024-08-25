import requests
import base64

# Mã hóa hình ảnh sang dạng base64
with open("maxresdefault.jpg", "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

# Thay thế data['image'] bằng encoded_string

KEY_API_GOOGLE = 'AIzaSyDNoZlY0D2a2xXxVfyAIXBMHsKZpqfd4YM'

url = f'https://vision.googleapis.com/v1/images:annotate?key={KEY_API_GOOGLE}'

request_data = {
    "requests": [
        {
            "image": {
                "content": encoded_string
            },
            "features": [
                {
                    "type": "TEXT_DETECTION"
                }
            ]
        }
    ]
}

response = requests.post(url, json=request_data)

if response.status_code == 200:
    try:
        response_text = response.json()['responses'][0]['fullTextAnnotation']['text']
        print(response_text)
    except KeyError:
        response_text = 'Không nhận diện được văn bản'
        print(response_text)
else:
    print(f'Error: {response.status_code}')
    print(response.json())
