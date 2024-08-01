import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import os
import json
import requests
import threading
from datetime import datetime, timedelta
import pytz
from selenium import webdriver
import shutil
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import os
import time
from selenium.webdriver.common.keys import Keys
from moviepy.editor import VideoFileClip
from selenium.common.exceptions import TimeoutException

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from requests.exceptions import RequestException
from requests.exceptions import RequestException
from urllib3.exceptions import ProtocolError
from urllib.parse import urlparse, unquote
from requests.exceptions import HTTPError

class SettingDialog(tk.Toplevel):
    def __init__(self, parent, selected_index, config_data):
        super().__init__(parent)
        self.root = parent
        self.title("Cài Đặt Profile")
        self.geometry("700x230")
        self.config_data = config_data
        self.selected_index = selected_index

        # Tìm giá trị cho self.count_upload_to_day và self.count_time_upload
        for profile in self.config_data['profiles']:
            if profile['name'] == selected_index:
                count_upload_to_day = profile['uploadLimitPerDay']
                path_profile = profile['path_profile']

        self.count_time_upload = config_data['timeupload']

        self.frame = ttk.Frame(self)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.titleLabel = ttk.Label(self.frame, text=f"Cài Đặt Profile {self.selected_index}", font=("Helvetica", 12, "bold"))
        self.titleLabel.grid(row=0, column=0, columnspan=3, pady=10)

        # URL Path
        self.urlLabel = ttk.Label(self.frame, text="URL Path:", font=("Helvetica", 10))
        self.urlLabel.grid(row=1, column=0, pady=5, sticky=tk.W)
        self.urlEntry = ttk.Entry(self.frame, font=("Helvetica", 10))
        self.urlEntry.grid(row=1, column=1, columnspan=2, pady=5, sticky=tk.EW)
        self.urlEntry.insert(0, path_profile)

        # Upload Time
        self.label_2 = ttk.Label(self.frame, text="UPLOAD TIME", font=("Helvetica", 10))
        self.label_2.grid(row=2, column=0, pady=5, sticky=tk.W)
        self.spinBox = tk.Spinbox(self.frame, font=("Helvetica", 10), from_=0, to=99)
        self.spinBox.grid(row=2, column=1, pady=5, sticky=tk.W)
        self.spinBox.config(width=5)  # Set width to 5 characters
        self.spinBox.delete(0, tk.END)
        self.spinBox.insert(0, self.count_time_upload)
        self.label = ttk.Label(self.frame, text="MINUTES", font=("Helvetica", 10))
        self.label.grid(row=2, column=2, pady=5, sticky=tk.W)

        # Uploads Per Day
        self.label_3 = ttk.Label(self.frame, text="UPLOADS PER DAY / Channel", font=("Helvetica", 10))
        self.label_3.grid(row=3, column=0, pady=5, sticky=tk.W)
        self.spinBox_2 = tk.Spinbox(self.frame, font=("Helvetica", 10), from_=0, to=20)
        self.spinBox_2.grid(row=3, column=1, pady=5, sticky=tk.W)
        self.spinBox_2.config(width=5)  # Set width to 5 characters
        self.spinBox_2.delete(0, tk.END)
        self.spinBox_2.insert(0, count_upload_to_day)
        self.label_4 = ttk.Label(self.frame, text="VIDEOS", font=("Helvetica", 10))
        self.label_4.grid(row=3, column=2, pady=5, sticky=tk.W)


        # Save Button
        self.pushButton = ttk.Button(self.frame, text="Lưu Cấu Hình", command=self.Button_save_configuration)
        self.pushButton.grid(row=5, column=0, columnspan=3, pady=5)

        self.frame.columnconfigure(1, weight=1)

        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        self.geometry("+%d+%d" % (parent.winfo_rootx() + parent.winfo_width() // 2 - self.winfo_width() // 2,
                                  parent.winfo_rooty() + parent.winfo_height() // 2 - self.winfo_height() // 2))
        
    def Button_save_configuration(self):
        for profile in self.config_data['profiles']:
            if profile['name'] == self.selected_index:
                profile['uploadLimitPerDay'] = int(self.spinBox_2.get())
                profile['path_profile'] = self.urlEntry.get()
                break  # Thoát vòng lặp sau khi đã cập nhật
        self.destroy()


class AddProfileDialog(tk.Toplevel):
    def __init__(self, parent, config_data):
        super().__init__(parent)
        self.geometry("500x300")
        self.title("Add New Profile")
        self.parent = parent

        self.config_data = config_data
        self.profile = None  
        
        # Dùng để lưu profile mới
        # Tạo frame chính để cải thiện bố cục
        main_frame = ttk.Frame(self)
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Label cho nhập tên hồ sơ
        self.profile_name_label = ttk.Label(main_frame, text="Profile Name:", font=("Arial",15))
        self.profile_name_label.pack(pady=(10,0))

        # Entry cho nhập tên
        self.profile_name_entry = ttk.Entry(main_frame, font=("Arial", 15))
        self.profile_name_entry.pack(pady=(10,0), fill=tk.X)


        # Label cho nhập url path profile
        self.path_profile_label = ttk.Label(main_frame, text="URL PROFILE", font=("Arial", 15))
        self.path_profile_label.pack(pady=(10,0))

        # Entry cho nhập  url path profile
        self.path_profile = ttk.Entry(main_frame, font=("Arial", 15))
        self.path_profile.pack(pady=(10,0), fill=tk.X)

        # Text widget để hiển thị hướng dẫn
        self.text_editor = tk.Text(main_frame, height=3, font=("Arial", 15), state='normal')
        self.text_editor.pack(pady=(10,0), fill=tk.BOTH, expand=True)
        self.text_editor.insert(tk.END, "Trong trình duyện \"Firefox \" nhập \"about:profiles\" \n vào thanh địa chỉ để lấy path profile \"Local Directory\" \n ")
        self.text_editor.config(state='disabled')  # Đặt trạng thái chỉ đọc sau khi thêm văn bản

        # Nút lưu
        self.save_button = ttk.Button(main_frame, text="Save", command=self.save_profile)
        self.save_button.pack(pady=(10,0), fill=tk.BOTH, expand=True)

        # Cập nhật thông tin kích thước và vị trí của widget
        self.update_idletasks()

        # Update the widget's size and position info
        self.geometry("+%d+%d" % (parent.winfo_rootx() + parent.winfo_width() // 2 - self.winfo_width() // 2,
                                  parent.winfo_rooty() + parent.winfo_height() // 2 - self.winfo_height() // 2))

    def save_profile(self):
        profile_name = self.profile_name_entry.get().strip()
        path_profile = self.path_profile.get().strip()
        if not profile_name or not path_profile:  # Kiểm tra nếu chuỗi đầu vào rỗng
            messagebox.showerror("Error", "VUi Lòng Điền đầy đủ thông tin")
            return
        

        for iteam in self.config_data['profiles']:
            if iteam['name'] == profile_name:
                messagebox.showerror("Error", "Profile đã tồn tại")
                return

        tz = pytz.timezone('Asia/Ho_Chi_Minh')
        current_time = datetime.now(tz)

        new_profile = {
            "name": profile_name,
            'path_profile': path_profile,
            "uploadsToday": 0,
            "lastUploadTime": current_time.strftime('%Y-%m-%d %H:%M:%S'),
            "uploadLimitPerDay": 6,
        }
        self.config_data['profiles'].append(new_profile)  # Đảm bảo rằng việc này an toàn với đa luồng
        self.destroy()

class Myapp:

    def __init__(self, root):
        self.root = root
        self.root.title("Main Window")
        self.root.geometry("1100x598")
        self.id = None

        self.create_widgets()
        self.is_start = False
        self.stop_thread = threading.Event()

        self.root.update_idletasks()  # Update the widget's size and position info
        self.root.geometry("+%d+%d" % (root.winfo_screenwidth() // 2 - self.root.winfo_width() // 2,
                                       root.winfo_screenheight() // 2 - self.root.winfo_height() // 2))
        self.get_ip_address()

        # Kiểm tra, tạo (nếu cần) và đọc tệp JSON
        self.config_data = self.check_and_create_json_file('config.json')

        self.url = self.config_data['url-sever']
        self.url_entry.delete(0, tk.END)  # Clear any existing text in the entry
        self.url_entry.insert(0, self.url)  # Insert the new text
            
        self.update_listbox_with_profiles()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing) 

    def create_widgets(self):
        self.centralwidget = tk.Frame(self.root)
        self.centralwidget.pack(fill=tk.BOTH, expand=True)
        self.create_input_frame()
        self.create_left_frame()
        self.create_right_frame()

    def create_input_frame(self):

        # Create a frame for the URL server input
        self.input_frame = tk.Frame(self.centralwidget)
        self.input_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        self.url_label = tk.Label(self.input_frame, text="URL Server:", font=("Arial", 16, "bold"))
        self.url_label.pack(side=tk.LEFT)

        self.url_entry = tk.Entry(self.input_frame, font=("Arial", 14))
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

    def create_left_frame(self):

        self.frame1 = tk.Frame(self.centralwidget)
        self.frame1.config(relief=tk.RAISED, width=700)
        self.frame1.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

        self.sub_frame1 = tk.Frame(self.frame1)
        self.sub_frame1.config(relief=tk.RAISED, height=50)
        self.sub_frame1.pack(side=tk.TOP, fill=tk.BOTH, expand=False)

        self.label_2 = tk.Label(self.sub_frame1, text="VPS IP:", font=("Arial", 16, "bold"))
        self.label_2.pack(side=tk.LEFT, padx=10)

        self.label_3 = tk.Label(self.sub_frame1, text="Đang lấy địa chỉ IP...", font=("Arial", 16, "bold"), fg="red")
        self.label_3.pack(side=tk.LEFT)

        self.copy_button = tk.Button(self.sub_frame1, text="Copy", font=("Arial", 10), command=self.copy_ip)
        self.copy_button.pack(side=tk.LEFT, padx=10)

        self.sub_frame2 = tk.Frame(self.frame1)
        self.sub_frame2.config(relief=tk.RAISED, height=60)
        self.sub_frame2.pack(side=tk.TOP, fill=tk.BOTH, expand=False)

        self.pushButton = tk.Button(self.sub_frame2, text="Add Profile", font=("Arial", 10),
                                    command=self.button_add_profile)
        self.pushButton.pack(side=tk.LEFT, padx=5, pady=5)

        self.pushButton_1 = tk.Button(self.sub_frame2, text="Delete Profile", font=("Arial", 10),
                                      command=self.button_delete_profile)
        self.pushButton_1.pack(side=tk.LEFT, padx=5, pady=5)

        self.pushButton_2 = tk.Button(self.sub_frame2, text="Open Profile", font=("Arial", 10),
                                      command=self.button_open_profile)
        self.pushButton_2.pack(side=tk.LEFT, padx=5, pady=5)

        self.pushButton_3 = tk.Button(self.sub_frame2, text="Setting", font=("Arial", 10), command=self.button_settings)
        self.pushButton_3.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.sub_frame4 = tk.Frame(self.frame1)
        self.sub_frame4.config(relief=tk.RAISED, height=60)
        self.sub_frame4.pack(side=tk.TOP, fill=tk.BOTH, expand=False)

        self.pushButton_4 = tk.Button(self.sub_frame4, text="Start", font=("Arial", 16), bg="green", fg="white", command=self.button_start)
        self.pushButton_4.pack(padx=5, pady=5)

        self.sub_frame5 = tk.Frame(self.frame1)
        self.sub_frame5.config(relief=tk.RAISED)
        self.sub_frame5.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.listbox = tk.Listbox(self.sub_frame5, font=("Arial", 16))
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Adding a new subframe for input and add button
        self.sub_frame6 = tk.Frame(self.frame1)
        self.sub_frame6.config(relief=tk.RAISED, height=50)
        self.sub_frame6.pack(side=tk.TOP, fill=tk.BOTH, expand=False, padx=5, pady=5)

    def create_right_frame(self):

        self.frame2 = tk.Frame(self.centralwidget)
        self.frame2.config(relief=tk.RAISED)
        self.frame2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.plainTextEdit = tk.Text(self.frame2, font=("Arial", 18), wrap=tk.WORD)
        self.plainTextEdit.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.scrollbar = tk.Scrollbar(self.plainTextEdit)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.plainTextEdit.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.plainTextEdit.yview)

    def button_add_profile(self):

        if not self.is_start:
            dialog = AddProfileDialog(self.root, self.config_data)
            self.root.wait_window(dialog)  # Chờ đến khi dialog được đóng
            self.update_listbox_with_profiles()  # Cập nhật listbox với dữ liệu mới
            self.save_config_data()
        else:
            messagebox.showinfo("Notification", "Hãy STOP lại trước khi thực hiện thay đổi")
    
    def button_delete_profile(self):

        if not self.is_start:
            selection = self.listbox.curselection()  # Lấy index của item được chọn
            if not selection:
                messagebox.showwarning("Warning", "Vui lòng chọn một profile để xóa !")
                return
            selected_index = selection[0]  # Giả sử chỉ chọn 1 profile để xoá
            profile_name = self.listbox.get(selected_index)  # Lấy tên profile

            # Xoá profile từ config_data
            for i, profile in enumerate(self.config_data['profiles']):
                if profile['name'] == profile_name:
                    del self.config_data['profiles'][i]
                    break  # Xoá và thoát vòng lặp
            self.update_listbox_with_profiles()  # Cập nhật lại listbox
            self.save_config_data()  # Lưu lại config_data
        else:
            messagebox.showinfo("Notification", "Hãy STOP lại trước khi thực hiện thay đổi")

    def button_open_profile(self):

        if not self.is_start:
            paths = [
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
            ]
            selection = self.listbox.curselection()  # Lấy index của item được chọn
            if not selection:
                messagebox.showwarning("Warning", "Vui lòng chọn một profile để mở!")
                return
            selected_index = selection[0]
            profile_name = self.listbox.get(selected_index)  # Lấy tên profile
            for profile in self.config_data['profiles']:
                if profile['name'] == profile_name:
                    path_profile = profile['path_profile']
                    for firefox_path in paths:
                        if os.path.exists(firefox_path):
                            command = [firefox_path, '-profile', path_profile]
                            try:
                                subprocess.run(command, check=True)
                            except subprocess.CalledProcessError as e:
                                messagebox.showerror("Error", f"Không thể mở profile: {e}")
                            break
                    else:
                        messagebox.showerror("Error", "Không tìm thấy đường dẫn tới Firefox.exe. Vui lòng kiểm tra lại.")
                    break
        else:
            messagebox.showinfo("Notification", "Hãy STOP lại trước khi thực hiện thay đổi")

    def button_settings(self):

        if not self.is_start:
            selection = self.listbox.curselection()
            if not selection:
                messagebox.showwarning("Warning", "Vui lòng chọn một hồ sơ để chỉnh sửa!")
                return
            selected_index = selection[0]
            profile_name = self.listbox.get(selected_index)
            dialog = SettingDialog(self.root, profile_name, self.config_data)
            self.root.wait_window(dialog)  # Chờ đến khi dialog được đóng
            self.update_listbox_with_profiles()  # Cập nhật listbox với dữ liệu mới
            self.save_config_data()
        else:
            messagebox.showinfo("Notification", "Hãy STOP lại trước khi thực hiện thay đổi")

    def button_start(self):

        self.url = self.url_entry.get()
        # Check if URL is empty
        if not self.url:
            messagebox.showerror("Error", "Vui Lòng Nhập Url Đường Dẫn SEVER")
            return
        self.save_config_data()

        if not self.is_start:
            self.pushButton_4.config(text="Stop", bg="red", fg="white")
            self.update_status_app("Server started...\n")
            self.url_entry.config(state='disabled')  # Disable the URL entry
            self.is_start = True
            self.thread = threading.Thread(target=self.run_server)
            self.thread.start()
        else:
            self.is_start = False
            self.pushButton_4.config(text="Start", bg="green", fg="white")
            self.update_status_app("Stopped, waiting to start...\n")
            self.url_entry.config(state='normal')  # Enable the URL entry
            if self.id is not None:
                self.update_status_video("Lỗi Upload: dừng sever")
            
    def run_server(self):
        while self.is_start:
            tz = pytz.timezone('Asia/Ho_Chi_Minh')
            current_time = datetime.now(tz)
            for profile in self.config_data['profiles']:
                last_upload_time = datetime.strptime(profile['lastUploadTime'], '%Y-%m-%d %H:%M:%S')
                last_upload_time = tz.localize(last_upload_time)
                #xóa bộ nhớ
                # self.clear_temp_folder()
                # Kiểm tra nếu đã qua một ngày mới và reset uploadsToday
                if current_time - last_upload_time >= timedelta(days=1) and self.is_start:
                    profile['uploadsToday'] = 0
                    profile['lastUploadTime'] = current_time.strftime('%Y-%m-%d %H:%M:%S')
                    self.save_config_data()
                # Kiểm tra nếu profile có thể upload thêm hôm nay
                if profile['uploadsToday'] < profile['uploadLimitPerDay'] and self.is_start:
                    self.update_status_app(f"profile {profile['name']} có thể tải lên ngay hôm nay.\n")
                    self.update_status_app(f"profile {profile['name']} Lấy thông tin upload...\n")
                    self.get_infor_video(profile)
                    time.sleep(3)
                    self.save_config_data()
                elif profile['uploadsToday'] == profile['uploadLimitPerDay'] and self.is_start:
                    self.update_status_app(f"profile {profile['name']} đã đạt đến giới hạn tải lên.\n")
                time.sleep(self.config_data['timeupload'])

    def get_infor_video(self, profile):
        data = {
                "ip_vps": self.ip_address,
                "action": "upload-video-to-vps",
                "channel_name": 'k1',
                "secret_key": "ugz6iXZ.fM8+9sS}uleGtIb,wuQN^1J%EvnMBeW5#+CYX_ej&%"
                }

        url = f'{self.url}api/'
        try:
            response = requests.post(url, json=data)
            infor_video = response.json()
            if 'message' in infor_video:
                self.update_status_app(f"profile {profile['name']}: {infor_video['message']}")
                return None
            
        except:
            self.update_status_app(f"lỗi kết nối đến server")
            return None
        self.handle_video_info(infor_video, profile)
        self.update_status_app(f"Đã lấy được thông tin chuẩn bị upload ...\n")
        self.update_status_video(f"Đang Upload Lên VPS : Đang Lấy Thông Tin Upload\n")
        if os.path.exists("Video_Upload"):
            shutil.rmtree("Video_Upload")
        os.makedirs("Video_Upload")



        self.create_or_reset_directory("Video_Upload")


        

        self.update_status_app(f"profile {profile['name']} đang tải video và thumnail \n")
        self.update_status_video(f"Đang Upload Lên VPS : Đang Tải Thumnail \n")

        url_thumnail  = infor_video["url_thumbnail"]
        file_thumnail = self.get_filename_from_url(url_thumnail)
        thumbnail_success = self.download_file(url_thumnail, "Video_Upload",
                                                file_thumnail)

        if thumbnail_success:
            self.update_status_video("Đang Upload Lên VPS : đã tải xong thumbnail")
            self.update_status_app(f"profile {profile['name']} đã tải xong thumbnail \n")
        else:
            self.update_status_video("Upload VPS Thất Bại : Lỗi tải thumbnail")
            self.update_status_app(f"profile {profile['name']} không tải được thumbnail \n")
            return
        
        url_video = infor_video["video_url"]
        file_video = self.get_filename_from_url(url_video)
        self.update_status_video("Đang Upload Lên VPS : Đang Tải Video")
        video_success = self.download_file(url_video, "Video_Upload",
                                            file_video)
        if video_success:
            self.update_status_video("Đang Upload Lên VPS : đã tải xong thumbnail")
            self.update_status_app(f"profile {profile['name']} đã tải xong video \n")
            self.upload_video_vps(profile)

        else:
            self.update_status_app(f"profile {profile['name']} không tải được video \n")
            self.update_status_video("Upload VPS Thất Bại : Không Tải Được Video")
            return
        
        self.upload_video_vps(profile)
    
    def handle_video_info(self, infor_video, profile):

        self.update_status_video("Đang Upload : lấy thông tin upload thành công")
        self.update_status_app(f"profile {profile['name']} Lấy thông tin thành công \n")
        self.id = infor_video["video_id"]
        self.title = infor_video["title"]
        self.description = infor_video["description"]
        self.keywords = infor_video["keywords"]


        self.date_uppic = infor_video["date_upload"]

        self.time_uppic = infor_video["time_upload"]
        self.thumbnail = self.get_filename_from_url(infor_video["url_thumbnail"])
        self.video_file =  self.get_filename_from_url(infor_video["video_url"])

    def upload_video_vps(self, profile):
        
        profile_path = profile['path_profile']
        options = Options()
        options.profile = webdriver.FirefoxProfile(profile_path)

      
        service = Service()  # Thay thế bằng đường dẫn tới geckodriver của bạn
        driver = webdriver.Firefox(service=service, options=options)


        driver.get('https://studio.youtube.com/')

        wait = WebDriverWait(driver, 10)
        self.update_status_video("Đang Upload Lên VPS : bắt đầu upload")
        self.update_status_app(f"profile {profile['name']} bắt đầu upload \n")

        try:
            if self.is_start:
                self.update_status_video("Đang Upload Lên VPS : Chuẩn bị upload lên kênh")
                button = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='upload-icon']/tp-yt-iron-icon")))
                button.click()

        except:
            self.update_status_video("Upload VPS Thất Bại : Kênh bị đăng xuất & bị die")
            self.update_status_app( f"profile {profile['name']} không đăng nhập bỏ qua \n")
            driver.quit()
            return
        
        if self.is_start:

            try:
                time.sleep(3)
                file_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="content"]/input')))
                video_file_name = os.path.basename(self.video_file)
                abs_path = os.path.abspath(os.path.join(os.getcwd(), 'Video_Upload', video_file_name))
                file_input.send_keys(abs_path)
                self.update_status_app(f"profile {profile['name']}  Upload xong video \n")
                self.update_status_video("Đang Upload Lên VPS : Đã Tải Lên Video")

            except Exception as e:
                self.update_status_app(f"Lỗi Upload video  \n")
                self.update_status_video("Upload VPS Thất Bại : Lỗi upload file Video")
                driver.quit()
                return

        if self.is_start:
            try:
                time.sleep(3)
                file_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="file-loader"]')))
                thumbnail_file_name = os.path.basename(self.thumbnail)
                abs_path = os.path.abspath(os.path.join(os.getcwd(), 'Video_Upload', thumbnail_file_name))
                file_input.send_keys(abs_path)
                self.update_status_video("Đang Upload Lên VPS : điền xong thumnail")
                self.update_status_app(f"profile {profile['name']}  Upload xong thumnail \n")
            except Exception as e:
                self.update_status_app(f"profile {profile['name']}  Lỗi Upload  thumnail \n ")
                self.update_status_video("Upload VPS Thất Bại : Lỗi upload file thumnail")
                driver.quit()
                return

        if self.is_start:
            try:
                time.sleep(3)
                file_input = wait.until(EC.element_to_be_clickable((By.ID, 'title-textarea')))
                time.sleep(2)
                driver.execute_script("arguments[0].innerText = '';", file_input)

                driver.execute_script("arguments[0].innerText = arguments[1];", file_input, self.title)
                self.update_status_video("Đang Upload Lên VPS : điền xong tiêu đề ")
                self.update_status_app(f"profile {profile['name']}  điền xong tiêu đề \n")
            except Exception as e:
                self.update_status_app(f"Lỗi tiêu đề {e}\n")
                self.update_status_video("Upload VPS Thất Bại : Lỗi điền tiêu đề ")
                driver.quit()
                return

        if self.is_start:
            try:
                time.sleep(3)
                file_input = wait.until(EC.element_to_be_clickable((By.ID,'description-textarea')))
                time.sleep(2)
                driver.execute_script("arguments[0].innerText = '';", file_input)

                driver.execute_script("arguments[0].innerText = arguments[1];", file_input, self.description)

                self.update_status_video("Đang Upload Lên VPS : điền xong mô tả")
                self.update_status_app(f"profile {profile['name']}  điền xong mô tả \n")
            except Exception as e:
                self.update_status_app(f"Lỗi điền miêu tả \n")
                self.update_status_video("Upload VPS Thất Bại: Lỗi điền  mô tả ")
                driver.quit()
                return

        if self.is_start:
            try:
                time.sleep(3)
                next_button = wait.until(EC.element_to_be_clickable((By.XPATH,
                                                                     '/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-ve/ytcp-video-metadata-editor/div/ytcp-video-metadata-editor-basics/div[5]/ytkc-made-for-kids-select/div[4]/tp-yt-paper-radio-group/tp-yt-paper-radio-button[2]/div[1]')))
                next_button.click()

                self.update_status_app(f"Đang tích trên 18 tuổi \n")
                self.update_status_video("Đang Upload Lên VPS : Đang Chọn Trên 18 Tuổi")
            except Exception as e:
                self.update_status_app(f"Lỗi chọn dưới 18 Tuổi \n")
                self.update_status_video("Upload VPS Thất Bại : Lỗi chọn dưới 18 Tuổi")
                driver.quit()
                return

        if self.is_start:
            try:
                time.sleep(3)
                upload_button = wait.until(EC.element_to_be_clickable((By.ID,'toggle-button')))
                upload_button.click()
            except Exception as e:
                self.update_status_app(f"Lỗi tìm kiếm phần tử tùy chọn keyworld \n")
                self.update_status_video("Upload VPS Thất Bại : Lỗi tìm kiếm phần tử tùy chọn keyworld")
                driver.quit()
                return
        
        if self.is_start:
            try:
                time.sleep(3)
                file_input = wait.until(EC.element_to_be_clickable((By.ID, 'text-input')))
                time.sleep(3)
                file_input.clear()
                file_input.send_keys(self.keywords)
                self.update_status_video("Đang Upload Lên VPS: điền xong  key world")
                self.update_status_app(f"profile {profile['name']}  điền xong  key world \n")
            except Exception as e:
                self.update_status_app(f"Lỗi điền keyworld\n")
                self.update_status_video("Upload VPS Thất Bại : lỗi điền keyworld")
                driver.quit()
                return

        if self.is_start:
            try:
                time.sleep(3)
                next_button = wait.until(EC.element_to_be_clickable((By.ID, 'next-button')))
                next_button.click()
            except Exception as e:
                self.update_status_app(f"Lỗi tìm kiếm nút next\n")
                self.update_status_video("Upload VPS Thất Bại  : lỗi tìm phần tử next")
                driver.quit()
                return


        if self.is_start:
            is_money = False
            self.update_status_video("Đang Upload Lên VPS: đang kiểm tra kênh bật kiếm tiền")
            try:
                time.sleep(3)
                self.update_status_app(f"đang kiểm tra chế độ bật kiếm tiền\n")
                next_button = wait.until(EC.element_to_be_clickable((By.ID, 'child-input')))
                next_button.click()
                is_money = True
            except:
                is_money = False
                self.update_status_app(f"kênh này không được bật kiếm tiền\n")

        if self.is_start and is_money:
            try:
                time.sleep(3)
                next_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="radio-on"]')))
                next_button.click()
                self.update_status_video("Đang Upload Lên VPS: Đang bật kiếm tiền")
                self.update_status_app(f"profile {profile['name']}  Đang bật kiếm tiền\n")
            except Exception as e:
                self.update_status_app(f"Lỗi chọn nút kiếm tiền \n")
                self.update_status_video("Upload VPS Thất Bại :Lỗi chọn nút kiếm tiền")
                driver.quit()
                return

        if self.is_start and is_money:
            try:
                time.sleep(3)
                next_button = wait.until(EC.element_to_be_clickable((By.ID, 'save-button')))
                next_button.click()
                time.sleep(6)
            except Exception as e:
                self.update_status_app(f"Lỗi chọn nút kiếm tiền \n")
                self.update_status_video("Upload VPS Thất Bại :Lỗi chọn nút kiếm tiền")
                driver.quit()
                return
        
        video_short = False

        if self.is_start and is_money:
            try:
                time.sleep(3)
                next_button = wait.until(EC.element_to_be_clickable((By.ID, 'place-manually-button')))
                next_button.click()
                video_short = True
                self.update_status_video("Đang Upload Lên VPS: Chuẩn bị đặt quảng cáo")
            except Exception as e:
                self.update_status_app(f"Video Ngắn Không Đặt Được Quảng cáo \n")
                self.update_status_video("Đang Upload Lên VPS : Video Ngắn Không Đặt Được Quảng cáo")
                video_short = False
        
        duration = None

        if self.is_start and is_money  and video_short:
            try:
                video_file_name = os.path.basename(self.video_file)
                duration = self.get_video_duration(os.path.join(os.getcwd(), 'Video_Upload', video_file_name))
            except Exception as e:
                self.update_status_app(f"Lỗi Đọc thời gian video \n")
                self.update_status_video("Upload VPS Thất Bại:Lỗi Đọc thời gian video")
                driver.quit()
                return
        
        if duration is not None and self.is_start and is_money and video_short:
            timestamps = self.generate_timestamps(duration)
            self.update_status_video("Đang Upload Lên VPS : Đangg Đặt Quảng cáo")
            for timestamp in timestamps:
                if self.is_start:
                    try:
                        input_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#left-controls input[type="text"]')))
                        input_element.click()  
                        input_element.send_keys(Keys.CONTROL + "a") 
                        input_element.send_keys(Keys.DELETE)
                        input_element.send_keys(timestamp)
                        save_button = wait.until(EC.element_to_be_clickable((By.ID, 'add-ad-break')))
                        save_button.click()
                        time.sleep(3)
                                                                
                    except Exception as e:
                        self.update_status_app( f"Lỗi chọn set quản cáo \n")
                        self.update_status_video("Upload VPS Thất Bại :Lỗi chọn set quảng cáo")
                        driver.quit()
                        return
            self.update_status_video("Đang Upload : Cài Đặt xong quảng cáo")
            self.update_status_app(f"profile {profile['name']} Cài Đặt xong quảng cáo\n")

        if self.is_start and is_money and video_short:
            try:
                time.sleep(3)
                save_button = wait.until(EC.element_to_be_clickable((By.ID, 'save-container')))
                save_button.click()
            except Exception as e:
                self.update_status_app(f"Lỗi lưu quản cáo \n")
                self.update_status_video("Upload VPS Thất Bại: Lỗi Lưu Quảng cáo")
                driver.quit()
                return

        if self.is_start and is_money:
            try:
                time.sleep(3)
                next_button = wait.until(EC.element_to_be_clickable((By.ID, 'next-button')))
                next_button.click()
            except Exception as e:
                self.update_status_app(f"Lỗi tìm gửi check quảng cáo \n")
                self.update_status_video("Upload VPS Thất Bại : Lỗi nhấn check quảng cáo")
                driver.quit()
                return

        if self.is_start and is_money:
            try:
                time.sleep(3)
                # Tìm phần tử checkbox
                checkbox = driver.find_element(By.XPATH, '/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-uploads-content-ratings/ytpp-self-certification-questionnaire/div[3]/div/ytcp-checkbox-lit/div/div[1]/div/div/div')
                driver.execute_script("arguments[0].scrollIntoView();", checkbox)
                ActionChains(driver).click(checkbox).perform()

            except Exception as e:
                self.update_status_app(f"lỗi tìm gửi check quản cáo \n")
                self.update_status_video("Upload VPS Thất Bại : Lỗi nhấn check box")
                driver.quit()
                return

        if self.is_start and is_money:
            try:
                time.sleep(3)
                next_button = wait.until(EC.element_to_be_clickable((By.ID, 'submit-questionnaire-button')))
                next_button.click()
                time.sleep(10)
            except Exception as e:
                self.update_status_app(f"lỗi nhấn phần tử \n")
                self.update_status_video("Upload VPS Thất Bại : Lỗi nhấn phần tử")
                driver.quit()
                return

        if self.is_start and is_money:
            try:
                time.sleep(3)
                next_button = wait.until(EC.element_to_be_clickable((By.ID, 'next-button')))
                next_button.click()
            except Exception as e:
                self.update_status_app(f"lỗi nhấn phần tử next \n")
                self.update_status_video("Upload VPS Thất Bại : Lỗi nhấn phần tử next lần 2")
                driver.quit()
                return

        if self.is_start:
            try:
                time.sleep(3)
                next_button = wait.until(EC.element_to_be_clickable((By.ID, 'next-button')))
                next_button.click()
            except Exception as e:
                self.update_status_app(f"lỗi nhấn phần tử next\n")
                self.update_status_video("Upload VPS Thất Bại : Lỗi nhấn phần tử next lần 3")
                driver.quit()
                return

        if self.is_start:
            try:
                time.sleep(3)
                next_button = wait.until(EC.element_to_be_clickable((By.ID, 'next-button')))
                next_button.click()
                time.sleep(6)
            except Exception as e:
                self.update_status_app(f"lỗi nhấn phần tử \n")
                self.update_status_video("Upload VPS Thất Bại : Lỗi nhấn phần tử lần 1")
                driver.quit()
                return

        if self.is_start:
            try:
                time.sleep(3)
                next_button = wait.until(EC.element_to_be_clickable((By.ID, 'second-container-expand-button')))
                next_button.click()
            except Exception as e:
                self.update_status_app(f"lỗi nhấn phần tử \n")
                self.update_status_video("Upload VPS Thất Bại : Lỗi nhấn phần tử lần 2")
                driver.quit()
                return

        if self.is_start:
            try:
                time.sleep(3)
                next_button = wait.until(EC.element_to_be_clickable((By.ID, 'datepicker-trigger')))
                next_button.click()
            except Exception as e:
                self.update_status_app(f"lỗi nhấn phần tử 3\n")
                self.update_status_video("Upload VPS Thất Bại : Lỗi nhấn phần tử lần 3")
                driver.quit()
                return

        if self.is_start:
            try:
                time.sleep(3)
                next_button = wait.until(EC.element_to_be_clickable((By.XPATH,
                                                                     '/html/body/ytcp-date-picker/tp-yt-paper-dialog/div/form/tp-yt-paper-input/tp-yt-paper-input-container/div[2]/div/iron-input/input')))
                next_button.click()

                # Lấy giá trị ngày tháng hiện tại
                current_date_value = next_button.get_attribute('value')
                print(f"Current date value in input: {current_date_value}")

                browser_date_format = self.get_browser_date_format(current_date_value)
                if not browser_date_format:
                    self.update_status_app(f"Không xác định được định dạng ngày của trình duyệt \n")
                    return 
            
                date = self.format_date_for_browser(self.date_uppic, browser_date_format)
                time.sleep(2)

                next_button.clear()
                next_button.send_keys(date)
                time.sleep(3)
                next_button.send_keys(Keys.RETURN)
                self.update_status_video("Đang Upload Lên VPS : Cài Đặt xong ngày uppic \n")
                self.update_status_app(f"profile {profile['name']} Cài Đặt xong ngày uppic \n")
            except Exception as e:
                self.update_status_app(f"ỗi cài đặt ngày uppic \n")
                self.update_status_video("Upload VPS Thất Bại : Lỗi cài đặt ngày uppic")
                driver.quit()
                return

        if self.is_start:
            try:
                time.sleep(3)
                next_button = wait.until(EC.element_to_be_clickable((By.XPATH,
                                                                     '/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-uploads-review/div[2]/div[1]/ytcp-video-visibility-select/div[3]/div[2]/ytcp-visibility-scheduler/div[1]/ytcp-datetime-picker/div/div[2]/form/ytcp-form-input-container/div[1]/div/tp-yt-paper-input/tp-yt-paper-input-container/div[2]/div/iron-input/input')))
                next_button.click()
                next_button.clear()
                time.sleep(2)
                next_button.send_keys(self.time_uppic)
                time.sleep(2)
                next_button.send_keys(Keys.RETURN)
                self.update_status_video("Đang Upload Lên VPS : Cài Đặt xong giờ Uppic\n")
                self.update_status_app(f"profile {profile['name']} Cài Đặt xong giờ Uppic \n")
            except Exception as e:
                self.update_status_app(f"Lỗi cài đặt giờ uppic  quá ngyaf upload\n")
                self.update_status_video("Upload VPS Thất Bại : Lỗi cài đặt giờ uppic")
                driver.quit()
                return
        if self.is_start:
            css_selector = 'span.progress-label.style-scope.ytcp-video-upload-progress'
            try:
                # Chờ đợi trong tối đa 900 giây cho đến khi một trong ba văn bản xuất hiện
                WebDriverWait(driver, 900).until(
                    EC.or_(
                        EC.text_to_be_present_in_element((By.CSS_SELECTOR, css_selector), "Upload complete"),
                        EC.text_to_be_present_in_element((By.CSS_SELECTOR, css_selector), "Processing up to HD"),
                        EC.text_to_be_present_in_element((By.CSS_SELECTOR, css_selector), "Checks complete.")
                    )
                )
            except Exception as e:
                pass

        if self.is_start:
            try:
                time.sleep(3)
                next_button = wait.until(EC.element_to_be_clickable((By.ID, 'done-button')))
                next_button.click()
            except Exception as e:
                self.update_status_app(f"Lỗi  nhấn lưu video \n")
                self.update_status_video("Upload VPS Thất Bại : Lỗi nhấn lưu video")
                driver.quit()
                return
            try:
                next_button = wait.until(EC.element_to_be_clickable((By.ID,'primary-action-button')))
                next_button.click()
            except:
                pass
            self.update_status_video('Upload VPS Thành Công')
            self.update_status_app(f"profile {profile['name']} upload thành công \n")
            profile['uploadsToday'] += 1
            self.id = None
            driver.quit()

    def get_browser_date_format(self,date_value):
        try:
            datetime.strptime(date_value, "%d/%m/%Y")
            return "%d/%m/%Y"
        except ValueError:
            try:
                datetime.strptime(date_value, "%m/%d/%Y")
                return "%m/%d/%Y"
            except ValueError:
                try:
                    datetime.strptime(date_value, "%b %d, %Y")
                    return "%b %d, %Y"
                except ValueError:
                    return None

    def format_date_for_browser(self,date_str, browser_format):
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime(browser_format)

    def get_video_duration(self, video_path):
        try:
            with VideoFileClip(video_path) as video:
                return video.duration
        except Exception as e:
            print(f"Error: {e}")
            return None

    def convert_seconds_to_time_format(self, duration_seconds, is_long_duration):
        hours = int(duration_seconds // 3600)
        minutes = int((duration_seconds % 3600) // 60)
        seconds = int(duration_seconds % 60)
        frames = 00  # Giả định khung hình là 00
        if is_long_duration:
            return f"{minutes:02}:{seconds:02}:{frames:02}"
        else:
            return f"{hours:02}:{minutes:02}:{seconds:02}:{frames:02}"

    def generate_timestamps(self, duration_seconds, start_seconds=3, interval_seconds=150):
        timestamps = []
        current_seconds = start_seconds
        is_long_duration = duration_seconds < 3600
        while current_seconds <= duration_seconds:
            formatted_time = self.convert_seconds_to_time_format(current_seconds, is_long_duration)
            timestamps.append(formatted_time)
            current_seconds += interval_seconds
        return timestamps

    def update_status_video(self, text):
        data = {
                "action": "update_status",
                "video_id": self.id,
                "status": text,
                "secret_key": "ugz6iXZ.fM8+9sS}uleGtIb,wuQN^1J%EvnMBeW5#+CYX_ej&%"
            }
        url = f'{self.url}api/'
        response = requests.post(url, json=data)
        infor_video = response.json()
        if 'message' in infor_video:
            return None

    def update_status_app(self, text):
        # Đặt múi giờ +7 (Ví dụ: Asia/Ho_Chi_Minh cho Việt Nam)
        timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        # Lấy thời gian hiện tại theo múi giờ +7
        current_time = datetime.now(timezone)
        # Lấy giờ và phút
        hour_minute = current_time.strftime('%H:%M:%S')
        self.plainTextEdit.insert(tk.END, f"{hour_minute} ----- {text}\n")
        self.plainTextEdit.see(tk.END)
        
    def get_ip_address(self):
        # Chạy quá trình lấy IP trong một luồng riêng để không block UI
        thread = threading.Thread(target=self.retrieve_ip_address)
        thread.start()

    def retrieve_ip_address(self):
        try:
            self.ip_address = requests.get('https://ipinfo.io/ip').text.strip()
            # Cập nhật IP address trên UI từ luồng chính
            self.label_3.config(text=self.ip_address)
        except Exception as e:
            self.ip_address = "Không thể lấy địa chỉ IP"

    def check_and_create_json_file(self, filename):
        if not os.path.exists(filename):
            # Lấy ngày giờ hiện tại và điều chỉnh múi giờ
            tz = pytz.timezone('Asia/Ho_Chi_Minh')  # Sử dụng múi giờ phù hợp với yêu cầu
            current_time = datetime.now(tz)
            # Dữ liệu mặc định để ghi vào tệp JSON mới
            data = {
                'url-sever': '',
                "timeupload": 0,
                "profiles": [],
            }
            with open(filename, 'w', encoding='utf-8') as json_file:
                json.dump(data, json_file, indent=4)
            return data  # Trả về dữ liệu mặc định
        else:
            # Nếu tệp tồn tại, đọc và trả về dữ liệu từ tệp
            with open(filename, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)
            return data  # Trả về dữ liệu đã đọc

    def update_listbox_with_profiles(self):
        if hasattr(self, 'listbox') and self.listbox.winfo_exists():
            self.listbox.delete(0, tk.END)
            sorted_profiles = sorted(self.config_data.get('profiles', []), key=lambda x: x['name'])
            for profile in sorted_profiles:
                self.listbox.insert(tk.END, profile['name'])

    def save_config_data(self, filename='config.json'):
        # Sắp xếp profiles trước khi lưu, nếu muốn duy trì thứ tự trong file JSON
        self.config_data['url-sever'] = self.url_entry.get()
        self.config_data['profiles'] = sorted(self.config_data.get('profiles', []), key=lambda x: x['name'])
        with open(filename, 'w', encoding='utf-8') as json_file:
            json.dump(self.config_data, json_file, indent=4)

    def clear_temp_folder(self):
        temp_directory = os.environ.get('TEMP')
        # Kiểm tra xem thư mục tồn tại hay không
        if temp_directory and os.path.exists(temp_directory):
            # Lấy danh sách các tệp tin trong thư mục
            file_list = os.listdir(temp_directory)

            # Xoá từng tệp tin
            for file_name in file_list:
                file_path = os.path.join(temp_directory, file_name)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"Error while deleting {file_path}: {e}")
        else:
            print(f"Temp directory '{temp_directory}' does not exist.")

    def download_file(self, url, directory, filename, retries=100):
        attempt = 0
        while attempt < retries:
            try:
                response = requests.get(url, stream=True)
                if response.status_code == 200:
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                    path = os.path.join(directory, filename)
                    with open(path, 'wb') as file:
                        response.raw.decode_content = True
                        shutil.copyfileobj(response.raw, file)
                    return True
                else:
                    print(f"Failed to download file: {response.status_code}")
                    return False
            except (RequestException, ProtocolError) as e:
                attempt += 1
                print(f"Attempt {attempt} failed: {e}")
                if attempt < retries:
                    print("Retrying...")
        print("Failed to download the file after multiple attempts")
        return False

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            if self.is_start:
                self.stop_thread.set()  # Đặt biến cờ để dừng thread
                self.thread.join()  # Đợi thread dừng hoàn toàn
            self.root.destroy()
            
    def get_filename_from_url(self,url):
        parsed_url = urlparse(url)
        path = unquote(parsed_url.path)
        filename = path.split('/')[-1]
        return filename

    def create_or_reset_directory(self,directory_path):
        try:
            # Kiểm tra xem thư mục có tồn tại hay không
            if os.path.exists(directory_path):
                # Kiểm tra xem thư mục có trống hay không
                if os.listdir(directory_path):
                    # Nếu không trống, xóa thư mục và toàn bộ nội dung bên trong
                    shutil.rmtree(directory_path)
                    print(f"Đã xóa thư mục '{directory_path}' và toàn bộ nội dung.")
                else:
                    # Nếu trống, chỉ xóa thư mục
                    os.rmdir(directory_path)
                    print(f"Đã xóa thư mục trống '{directory_path}'.")
            # Tạo lại thư mục
            os.makedirs(directory_path)
            return True
        except Exception as e:
            print(f"Lỗi: {e}")
            return False

    def copy_ip(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.label_3.cget("text"))

if __name__ == "__main__":
    root = tk.Tk()
    app = Myapp(root)
    root.mainloop()