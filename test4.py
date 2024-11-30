import requests

def audio_query_form_data(text, voice, speed, pitch, url):
    # Dữ liệu cần gửi dưới dạng form data
    data = {
        'text': text,
        'voice': voice,
        'speed': speed,
        'pitch': pitch
    }

    # Gửi yêu cầu POST với form data
    response = requests.post(url, data=data)

    # Kiểm tra mã trạng thái HTTP
    if response.status_code == 200:
        print("Yêu cầu thành công!")
        return response.content  # Dữ liệu trả về từ API (có thể là âm thanh hoặc JSON)
    else:
        print(f"Yêu cầu thất bại, mã lỗi: {response.status_code}")
        return None

if __name__ == "__main__":
    # Các tham số đầu vào
    text = "動画にナレーションやセリフを入れる際、ナレーターに依頼したり、自分の声を録音したりすると、予想以上に時間やコストがかかってしまうことも多いのではないでしょうか。"
    voice = "ja-JP-Takumi-NTTS"
    speed = 1
    pitch = 0

    # URL API (thay thế với URL đúng của bạn)
    url = "https://ondoku3.com/ja/text_to_speech/"

    # Gửi yêu cầu và nhận kết quả
    result = audio_query_form_data(text, voice, speed, pitch, url)

    if result:
        # Nếu có kết quả, lưu vào tệp
        with open("audio_output.wav", "wb") as f:
            f.write(result)
        print("Âm thanh đã được lưu vào audio_output.wav")
