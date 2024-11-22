import requests

# Payload dữ liệu
payload = [
    {
        "text": "The government’s rule tries to ensure if one political candidate gains airtime on a broadcast station, then the candidate’s opponents can request an equal opportunity.",
        "actor_id": "62203cf8a08b67aac4623e41",
        "tempo": 1,
        "pitch": 0,
        "style_label": "angry-1",
        "style_label_version": "v5",
        "emotion_label": "angry",
        "emotion_scale": 1,
        "lang": "auto",
        "mode": "one-vocoder",
        "retake": True,
        "bp_c_l": True,
        "adjust_lastword": 0,
    }
]

# URL API
url = "https://typecast.ai/api/speak/batch/post"

# Headers với token hợp lệ
headers = {
    "authorization": "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IjkyODg2OGRjNDRlYTZhOThjODhiMzkzZDM2NDQ1MTM2NWViYjMwZDgiLCJ0eXAiOiJKV1QifQ.eyJuYW1lIjoiVHVuZyBkYW5nIiwicGljdHVyZSI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FHTm15eGIzZWg4cjAzYmNqRkxkT3ZIcFpNeDZPOWR3TVdFYWk3X18tWXdLPXM5Ni1jIiwiX2lkIjoiNjQ1NTQ0ZDFiYzI5M2FhYjQzZmZhMWE2IiwiYXBwcm92ZWQiOnRydWUsImF1dGh0eXBlIjoiZmlyZWJhc2UiLCJwcm92aWRlciI6InBhc3N3b3JkIiwiaXNzIjoiaHR0cHM6Ly9zZWN1cmV0b2tlbi5nb29nbGUuY29tL3R5cGVjYXN0LXByb2QtNTBjYjEiLCJhdWQiOiJ0eXBlY2FzdC1wcm9kLTUwY2IxIiwiYXV0aF90aW1lIjoxNzMyMjc0NzkxLCJ1c2VyX2lkIjoiRzVGOHB0cWJPZVRCeU4xV0N5dHJqanRlWGRkMiIsInN1YiI6Ikc1RjhwdHFiT2VUQnlOMVdDeXRyamp0ZVhkZDIiLCJpYXQiOjE3MzIyNzQ3OTEsImV4cCI6MTczMjI3ODM5MSwiZW1haWwiOiJkYW5ndHVuZ21lZGlhQGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJmaXJlYmFzZSI6eyJpZGVudGl0aWVzIjp7ImVtYWlsIjpbImRhbmd0dW5nbWVkaWFAZ21haWwuY29tIl19LCJzaWduX2luX3Byb3ZpZGVyIjoiY3VzdG9tIn19.Ev6E9M1fIQQKX9BSZX30qbyB3k9glEhGpZxhRmWUX_rX8CZqmepQ4j445OtsLAuA6jzkFaAIG-u2wq7vozHWj2FSS_8t36WGOzRdCqo_Y3JPPl-646_ItF9-zOG966zb5vaRM0YxIivbMyymz1hXiE3bLPOpopB9gQPE_V1ZYM7oYde2lLBhzbqAgTlpctLdsmrXkjsgNwNxUIkFjnlFrrfPVnxHSmIHpw7AUwm4MzvqjSVCpC4t1TTToDIBlPxuA_E0GA_hriKcGQWCzahCUvNBz1As8CjuAYC3KurEh77WzxmWLfhtSbfdVNI2GMkurXjmhzk7hbB4ryzh4tZtvg",  # Thay <your_access_token> bằng token của bạn
    "Content-Type": "application/json"
}

# Thực hiện yêu cầu POST
response = requests.post(url, json=payload, headers=headers)

# In phản hồi từ API
print(response.status_code)  # Mã trạng thái phản hồi
print(response.text)         # Nội dung phản hồi
