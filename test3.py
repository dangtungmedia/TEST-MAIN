import requests
import json

def audio_query(text, speaker_id=1, core_version=1):
    # URL API với các tham số trong URL
    url = f"http://127.0.0.1:50021/audio_query?speaker={speaker_id}&core_version={core_version}"

    # Header yêu cầu trả về JSON
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',  # Đảm bảo Content-Type là application/json
    }

    # Dữ liệu gửi đi (body yêu cầu), ở đây 'text' là văn bản bạn muốn xử lý
    data = {
        'text': text
    }

    try:
        # Gửi yêu cầu POST
        response = requests.post(url, headers=headers, json=data)

        # Kiểm tra nếu có lỗi HTTP
        response.raise_for_status()

        # Trả về JSON từ phản hồi
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Đã xảy ra lỗi khi gửi yêu cầu: {e}")
        return None

if __name__ == "__main__":
    text = "GPU 版を利用する場合、環境によってエラーが発生することがあります。"  # Văn bản bạn muốn chuyển đổi thành giọng nói
    speaker_id = 1  # ID của speaker
    core_version = 1  # Phiên bản core API (nếu cần)

    result = audio_query(text, speaker_id, core_version)

    if result:
        print("Kết quả từ audio_query:")
        print(json.dumps(result, ensure_ascii=False, indent=4))
