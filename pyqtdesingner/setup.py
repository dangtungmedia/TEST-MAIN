from cx_Freeze import setup, Executable
include_files = ['VC_redist.x64.exe']
include_packages = ['selenium','pytz','moviepy','requests','PyQt6']
setup(
    name="App-upload-pro",
    version="1.0",
    description="Mô tả ứng dụng",
    executables=[Executable("app_upload.py", base="Win32GUI",icon="logo.ico")],
    options={"build_exe": {"include_files": include_files,
                           'packages':include_packages}}
)