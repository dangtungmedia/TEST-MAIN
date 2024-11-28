import json
import random

# Hàm để chọn nhiều video sao cho tổng duration lớn hơn thời gian nhập vào
def select_videos_by_total_duration(file_path, min_duration):
    # Đọc dữ liệu từ tệp JSON
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    total_duration = 0
    selected_urls = []

    # Tiến hành chọn ngẫu nhiên các video cho đến khi tổng duration lớn hơn min_duration
    while total_duration <= min_duration:
        # Chọn ngẫu nhiên một video từ danh sách
        video = random.choice(data)
        
        # Cộng thêm duration vào tổng duration
        total_duration += video['duration']
        
        # Thêm url vào danh sách các URL
        selected_urls.append(video['url'])  # Lấy URL của video
        
        # Loại bỏ video đã chọn khỏi danh sách để không chọn lại
        data.remove(video)
    
    return selected_urls

# Nhập thời gian từ người dùng
min_duration = int(input("Nhập thời gian (duration) tối thiểu: "))

# Gọi hàm để chọn video
result_urls = select_videos_by_total_duration('filtered_data.json', min_duration)

# In kết quả
if result_urls:
    print("Danh sách các URL video đã chọn:")
    for url in result_urls:
        print(url)
else:
    print("Không có video nào phù hợp.")
