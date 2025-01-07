import re

def remove_invalid_chars(string):
    # Kiểm tra nếu đầu vào không phải chuỗi
    if not isinstance(string, str):
        return ''
    # Loại bỏ ký tự Unicode 4 byte
    return re.sub(r'[^\u0000-\uFFFF]', '', string)

# Dữ liệu đầu vào
data = {'title': "Hello 🌟🌍! 안녕하세요💖"}

# Xử lý title
title = data.get('title', '')
clean_title = remove_invalid_chars(title)

print(clean_title)
