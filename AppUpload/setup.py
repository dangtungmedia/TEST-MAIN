from cx_Freeze import setup, Executable
import sys

# Thông tin về file chính của bạn
base = None
if sys.platform == "win32":
    base = "Win32GUI"

executables = [Executable(
    script="upload.py",# Tên file chính của bạn
    icon="logo.ico",# Đường dẫn đến file icon của bạn
    base=base
)]

# Thư viện cần thiết
build_exe_options = {
    "packages": ["os", "selenium", "requests", "tkinter", "pytz", "moviepy",'shutil',], # Thêm các gói cần thiết ở đây
    "include_files": ['VC_redist.x64.exe','logo.ico'] # Các file bổ sung cần thiết cho ứng dụng của bạn
}

setup(
    name="APP_UPLOAD",
    version="0.1",
    description="APP Upload",
    options={"build_exe": build_exe_options},
    executables=executables
)
#update code