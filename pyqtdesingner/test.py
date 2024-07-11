import requests

url = 'http://127.0.0.1:8000/get-video-content/'
my_data = {'id': 1, 'id_profile': 1}

response = requests.post(url, data=my_data)
print(response.text)