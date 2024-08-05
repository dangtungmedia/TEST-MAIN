import os

def find_font_file(font_name, font_dir, extensions=[".ttf", ".otf", ".woff", ".woff2"]):
    for root, dirs, files in os.walk(font_dir):
        for file in files:
            if any(file.lower() == f"{font_name.lower()}{ext}" for ext in extensions):
                return os.path.join(root, file)
    return None

# Giả sử bạn có tên font và thư mục chứa font
font_name = "Black Han Sans"
font_dir = "font"  # Thư mục chứa font

font_file = find_font_file(font_name, font_dir)
print(font_file)  # Đường dẫn đến file font