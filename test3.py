# Hàm thử lại với decorator

import requests


def retry(retries=3, delay=2):
    """
    Decorator để tự động thử lại nếu hàm gặp lỗi.
    
    Args:
        retries (int): Số lần thử lại tối đa.
        delay (int): Thời gian chờ giữa các lần thử (giây).

    Returns:
        Kết quả trả về từ hàm nếu thành công, None nếu thất bại.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(1, retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Lỗi trong {func.__name__}, lần thử {attempt}: {e}")
                    if attempt < retries:
                        print(f"Thử lại sau {delay} giây...")
                        time.sleep(delay)
                    else:
                        print(f"{func.__name__} thất bại sau {retries} lần thử.")
                        return None
        return wrapper
    return decorator

@retry(retries=3, delay=2)
def active_token(access_token):
    """
    Lấy idToken từ access_token.
    """
    Params = {
        "key": "AIzaSyBJN3ZYdzTmjyQJ-9TdpikbsZDT9JUAYFk"
    }
    data = {
        "token": access_token,
        "returnSecureToken": True
    }
    response = requests.post(
        'https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken',
        params=Params,
        json=data
    )
    response.raise_for_status()
    return response.json()['idToken']

@retry(retries=3, delay=2)
def get_access_token(idToken):
    """
    Lấy access_token từ idToken.
    """
    data = {
        "token": idToken
    }
    response = requests.post(
        'https://typecast.ai/api/auth-fb/custom-token',
        json=data
    )
    response.raise_for_status()
    return response.json()["result"]['access_token']

@retry(retries=3, delay=2)
def login_data(email, password):
    """
    Lấy idToken bằng cách đăng nhập với email và password.
    """
    data = {
        "returnSecureToken": True,
        "email": email,
        "password": password,
        "clientType": "CLIENT_TYPE_WEB"
    }
    Params = {
        "key": "AIzaSyBJN3ZYdzTmjyQJ-9TdpikbsZDT9JUAYFk"
    }
    url = 'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword'
    response = requests.post(url, params=Params, json=data)
    response.raise_for_status()
    return response.json()['idToken']

def get_cookie(email, password, access_token=None):
    """
    Kết hợp các bước:
    1. Đăng nhập để lấy idToken nếu access_token không được cung cấp.
    2. Lấy idToken từ active_token nếu access_token có sẵn.
    3. Lấy access_token từ idToken và lưu vào biến toàn cục.

    Args:
        email (str): Email đăng nhập.
        password (str): Mật khẩu đăng nhập.
        access_token (str, optional): Access token nếu đã có sẵn.

    Returns:
        str: Access token (cookie) nếu thành công, None nếu thất bại.
    """
    global ACCESS_TOKEN  # Khai báo biến toàn cục
    try:
        
        Token_login = login_data(email, password)

        idToken = get_access_token(Token_login)  # Lưu vào biến toàn cục
        
        ACCESS_TOKEN = active_token(idToken)
        
        print(ACCESS_TOKEN)
    except Exception as e:
        ACCESS_TOKEN = None
        print(f"Lỗi khi lấy cookie: {e}")
        


ACCESS_TOKEN = None
if __name__ == "__main__":
    get_cookie("dangtungmedia@gmail.com","@@Hien17987")