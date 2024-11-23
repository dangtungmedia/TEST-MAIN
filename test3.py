import requests
import ssl
import nltk
from googletrans import Translator
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk import ne_chunk
import random,time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Bỏ qua lỗi SSL tạm thời
ssl._create_default_https_context = ssl._create_unverified_context

# Khởi tạo đối tượng Translator
translator = Translator()

def extract_keywords_from_text(text):
    # Dịch văn bản sang tiếng Anh
    translated = translator.translate(text, src='vi', dest='en')

    # Câu cần phân tích
    sentence = translated.text

    # Tokenize câu thành các từ
    tokens = word_tokenize(sentence)

    # Gán nhãn phần loại từ (POS tagging)
    tags = pos_tag(tokens)

    # Nhận dạng thực thể (NER)
    named_entities = ne_chunk(tags)

    # Tìm các từ quan trọng (ví dụ, danh từ, tính từ, động từ)
    important_words = [word for word, pos in tags if pos in ['NN', 'NNS', 'NNP', 'NNPS', 'JJ', 'VB']]

    # Trả về các từ khóa tìm được (danh từ, tính từ, động từ)
    return important_words

def get_images_by_keyword(keyword):
    # URL của API
    url = "https://www.freepik.com/api/regular/search"
    
    # Các tham số cần thiết
    params = {
        "filters[ai-generated][only]": 1,  # Chỉ lấy các hình ảnh được tạo bởi AI
        "filters[content_type]": "photo",  # Chỉ lấy ảnh
        "filters[license]": "free",  # Chỉ lấy hình ảnh miễn phí
        "locale": "en",  # Ngôn ngữ là tiếng Anh
        "term": keyword,  # Tìm kiếm với từ khóa nhập vào
    }

    # Gửi yêu cầu GET
    response = requests.get(url, params=params)

    # Kiểm tra mã trạng thái và lấy dữ liệu nếu thành công
    if response.status_code == 200:
        data = response.json()  # Chuyển đổi nội dung trả về sang định dạng JSON
        list_images = []

        for item in data.get("items", []):
            preview = item.get("preview", {})
            width = preview.get("width")
            height = preview.get("height")
            
            # Kiểm tra ảnh ngang (width > height)
            if width and height and width > height:
                list_images.append(preview.get("url"))

        # Trả về danh sách ảnh ngang
        return list_images
    else:
        print(f"Error: {response.status_code}")
        return []

def get_pixabay_videos(query, duration, width=1920, height=1080):
    # URL của API Pixabay
    url = "https://pixabay.com/api/videos/"
    api_key = "47229269-2864f80175288bc6a290dd9c5"  # Thay thế bằng API key của bạn
    
    # Các tham số yêu cầu
    params = {
        "key": api_key,  # API Key
        "q": query,  # Từ khóa tìm kiếm
        "per_page": 200,  # Số lượng video trên mỗi trang
    }
    
    # Gửi yêu cầu GET tới API
    response = requests.get(url, params=params)
    
    # Kiểm tra mã trạng thái và lấy dữ liệu nếu thành công
    if response.status_code == 200:
        data = response.json()  # Chuyển đổi nội dung trả về sang định dạng JSON
        
        # Kiểm tra nếu có kết quả
        if "hits" in data:
            video_list = []
            
            # Duyệt qua các video và lấy thông tin cần thiết
            for item in data["hits"]:
                # Lấy thông tin về video với kích thước nhỏ nhất (small)
                small_video = item["videos"].get("small", {})
                video_width = small_video.get("width")
                video_height = small_video.get("height")
                
                # Kiểm tra nếu kích thước video là 1920x1080
                if video_width == width and video_height == height and duration <= int(item["duration"]):
                    video_url = small_video.get("url")
                    video_list.append(video_url)
            return video_list
        else:
            print("Không tìm thấy video nào.")
            return []
    else:
        print(f"Error: {response.status_code}")
        return []

def reading_time(text):
    # Tốc độ đọc trung bình (từ mỗi phút)
    words_per_minute = 250  # Có thể thay đổi thành 250 hoặc giá trị khác tùy theo yêu cầu
    
    # Tokenize văn bản thành các từ
    words = nltk.word_tokenize(text)
    
    # Đếm số từ trong văn bản
    num_words = len(words)
    
    # Tính toán thời gian đọc (thời gian đọc = số từ / tốc độ đọc)
    time_in_minutes = num_words / words_per_minute
    
    # Chuyển đổi thành phút và giây
    minutes = int(time_in_minutes)
    seconds = int((time_in_minutes - minutes) * 60)
    
    return minutes, seconds  # Trả về thời gian đọc dưới dạng phút và giây

def generate_random_content(data_file):
    # Đọc nội dung từ file
    with open(data_file, 'r') as file:
        data = file.read()

    # Loại bỏ các dòng trống và cắt bỏ khoảng trắng thừa
    lines = [line.strip() for line in data.split('\n') if line.strip()]

    # Tổng số phần tử
    total_items = len(lines)

    # Tính số lượng hình ảnh (60%) và video (40%)
    num_images = int(total_items * 0.6)  # 60% là hình ảnh
    num_videos = total_items - num_images  # 40% còn lại là video

    # Tạo dãy số cho hình ảnh và video
    images = ['image'] * num_images
    videos = ['video'] * num_videos

    # Gộp dãy hình ảnh và video
    all_items = images + videos

    # Random hóa dãy
    random.shuffle(all_items)

    # Khởi tạo cấu trúc JSON
    data_json = {}

    # Duyệt qua từng phần tử đã random và gán URL tương ứng
    with ThreadPoolExecutor(max_workers=1) as executor:  # Tăng số lượng luồng lên 50
        futures = []
        for i, item in enumerate(all_items, 1):
            text_content = lines[i - 1]
            futures.append(executor.submit(process_item, item, i, text_content))

        for future in as_completed(futures):
            result = future.result()
            if result:
                index, json_data = result
                data_json[index] = json_data

    return data_json

def process_item(item, index, text_content):
    # Xử lý từng mục (hình ảnh hoặc video)
    duration = reading_time(text_content)
    if item == 'image':
        keyword = extract_keywords_from_text(text_content)
        list_images = []
        for word in keyword:
            images = get_images_by_keyword(word)
            list_images.extend(images)
        url = random.choice(list_images) if list_images else 'No image found'
    elif item == 'video':
        keyword = extract_keywords_from_text(text_content)
        list_videos = []
        for word in keyword:
            videos = get_pixabay_videos(word, duration[0])
            list_videos.extend(videos)
        url = random.choice(list_videos) if list_videos else 'No video found'

    # Tạo JSON cho từng mục
    json_data = {
        'url': url,
        'content': text_content,
    }
    return index, json_data

# Gọi hàm và in kết quả
# Đo thời gian bắt đầu
start_time = time.time()

# Gọi hàm generate_random_content
data_json = generate_random_content('data.txt')

# Đo thời gian kết thúc
end_time = time.time()

# Tính thời gian hoàn thành
elapsed_time = end_time - start_time

# In kết quả
print(f"Thời gian hoàn thành: {elapsed_time:.2f} giây")
print(data_json)
