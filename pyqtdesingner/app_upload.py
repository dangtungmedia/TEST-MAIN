import json
import os
import shutil
import time
from datetime import datetime, timedelta

import pytz
import requests
from moviepy.editor import VideoFileClip
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager

from addprofile import Ui_Form
from myapp import Ui_MainWindow
from setting import Ui_Form_setting



class From_add_profile(QDialog):
    def __init__(self,url,config):
        super().__init__()
        self.uic = Ui_Form()
        self.uic.setupUi(self)
        self.setWindowTitle('My Application')
        self.url = f"{url}api/topics/"
        self.config = config
        self.load_data()
        self.uic.pushButton.clicked.connect(self.button_save_profile)

    def load_data(self):
        response = requests.get(self.url).json()
        for item in response:
            self.uic.comboBox.addItem(item['name_toppic_keyword'], item['id'])
        self.uic.comboBox.currentIndexChanged.connect(self.on_combobox_changed)

        if self.uic.comboBox.count() > 0:
            self.on_combobox_changed(0)

    def on_combobox_changed(self, index=-1):
        self.uic.comboBox_2.clear()
        id = self.uic.comboBox.itemData(index)
        if id is not None:
            response = requests.post(self.url, json={'id': id}).json()['profile']
            for item in response:
                self.uic.comboBox_2.addItem(item['name_profile_channel'], item['id'])

    def button_save_profile(self):
        if self.uic.lineEdit.text():
            if self.uic.comboBox.count() > 0 and self.uic.comboBox_2.count() > 0:
                id = self.uic.comboBox.itemData(self.uic.comboBox.currentIndex())
                name_folder = self.uic.comboBox.currentText()
                
                id_profile = self.uic.comboBox_2.itemData(self.uic.comboBox_2.currentIndex())
                name_profile = self.uic.comboBox_2.currentText()
                
                path = self.uic.lineEdit.text()
                
                tz = pytz.timezone('Asia/Ho_Chi_Minh')
                current_time = datetime.now(tz)
                formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
                
                # Tìm folder với ID cụ thể
                existing_folder = next((item for item in self.config['folder'] if item['id'] == id), None)

                if existing_folder is None:
                    # Nếu folder id không tồn tại, thêm folder mới
                    self.config['folder'].append({
                        'id': id,
                        'name': name_folder,
                        'profiles': [
                            {
                                'id': id_profile,
                                'name': name_profile,
                                'count_upload_today': 0,
                                'limit_upload_today': 6,
                                'date_upload': formatted_time,
                                'path_profile': path
                            }
                        ]
                    })
                    QMessageBox.information(self, 'Success', 'Folder and Profile added successfully.')
                    self.accept()
                    # Giả sử bạn có một hàm để lưu cấu hình vào file sau mỗi lần cập nhật
                else:
                    # Kiểm tra xem profile đã tồn tại trong folder này chưa
                    existing_profile = next((p for p in existing_folder['profiles'] if p['id'] == id_profile), None)

                    if existing_profile is None:
                        # Nếu profile chưa tồn tại, thêm mới vào folder hiện tại
                        existing_folder['profiles'].append({
                            'id': id_profile,
                            'name': name_profile,
                            'count_upload_today': 0,
                            'limit_upload_today': 6,
                            'date_upload': formatted_time,
                            'path_profile': path
                        })
                        QMessageBox.information(self, 'Success', 'Profile added successfully.')
                        self.accept()
                        # Lưu cấu hình
                    else:
                        # Nếu profile đã tồn tại, hiển thị thông báo
                        QMessageBox.warning(self, 'Warning', 'This profile already exists in the folder.')
            else:
                QMessageBox.warning(self, 'Warning', 'Please select a folder and a profile.')
        else:
            QMessageBox.warning(self, 'Warning', 'Please enter the Profile Path.')

class From_setting_profile(QDialog):
    def __init__(self, selected, config):
        super().__init__()
        self.uic = Ui_Form_setting()  # Giả sử Ui_Form_setting là một lớp được tự động tạo từ file .ui của PyQt
        self.uic.setupUi(self)
        
        self.config = config
        self.selected = selected
        self.load_data()
        self.uic.pushButton.clicked.connect(self.button_save_profile)

    def load_data(self):  # Sửa lỗi chính tả ở đây
        self.uic.label.setText("CÀI ĐẶT PROFILE :   " + self.selected)
        folder_name, profile_name = self.selected.split(' --- ')
        for forder in self.config['folder']:
            if forder['name'] == folder_name:
                for profile in forder['profiles']:
                    if profile['name'] == profile_name:
                        self.uic.lineEdit.setText(profile['path_profile'])
                        self.uic.spinBox.setValue(profile['limit_upload_today'])
                        break
    
    def button_save_profile(self):
        folder_name, profile_name = self.selected.split(' --- ')
        for forder in self.config['folder']:
            if forder['name'] == folder_name:
                for profile in forder['profiles']:
                    if profile['name'] == profile_name:
                        profile['path_profile'] = self.uic.lineEdit.text()
                        profile['limit_upload_today'] = self.uic.spinBox.value()
                        break
        QMessageBox.information(self, 'Success', 'Profile settings saved successfully.')
        self.accept()

class ServerThread(QThread):
    update_signal = pyqtSignal(object)
    def __init__(self):
        super().__init__()
        with open("config.json", "r",encoding='utf-8') as f:
                self.config = json.load(f)
        self.url = self.config['url']
        self.running = True

    def run(self):
        while self.running:
            tz = pytz.timezone('Asia/Ho_Chi_Minh')
            current_time = datetime.now(tz)
            for folder in self.config['folder']:
                for profile in folder['profiles']:
                    last_upload_time = datetime.strptime(profile['date_upload'], '%Y-%m-%d %H:%M:%S')
                    last_upload_time = tz.localize(last_upload_time)
                    time_difference = current_time - last_upload_time
                    self.clear_temp_folder()
                    if (time_difference >= timedelta(days=1)  )and self.running:
                        profile['count_upload_today'] = 0
                        profile['date_upload'] = current_time.strftime('%Y-%m-%d %H:%M:%S')
                        self.update_signal.emit(f"cập nhập lại số lần upload profile {folder['name']} --- {profile['name']} ")
                    if (profile['count_upload_today'] < profile['limit_upload_today'])and self.running:
                        self.update_signal.emit(f"Đang Lấy thông tin của {folder['name']} --- {profile['name']}")
                        if self.get_video_upload(folder,profile):
                            self.upload_video_to_channel(profile)

                    elif profile['count_upload_today'] == profile['limit_upload_today'] and self.running:
                        self.update_signal.emit(f"Profile {profile['name']} đã đạt đến giới hạn tải lên.\n")
                    time.sleep(1)
                    self.save_data()
               
    def upload_video_to_channel(self,profile):
        if os.path.exists("Video_Upload"):
            shutil.rmtree("Video_Upload")
        os.makedirs("Video_Upload")
        self.update_signal.emit("Đang Upload :Download video...")
        self.download_video()
        self.update_signal.emit("Download video success")
        self.upload_video(profile)

    def upload_video(self,data_profile):
        self.update_signal.emit("Bắt đầu Upload video\n")
        self.update_status_video("Đang Upload : Bắt đầu upload video")
        options = Options()
        profile = FirefoxProfile(profile_directory=rf"{data_profile['path_profile']}")
        options.add_argument("--start-maximized")
        options.profile = profile
        driver = webdriver.Firefox(options=options)  
        driver.get('https://studio.youtube.com/')
        wait = WebDriverWait(driver, 10)
        self.update_status_video("Đang Upload : mở profile firefox")
        try:
            if self.running:
                button = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='upload-icon']/tp-yt-iron-icon")))
                button.click()
        except Exception as e:
            self.update_signal.emit(e)
            self.update_signal.emit(f"Profile {data_profile['name']} không thể upload ")
            self.update_status_video("Lỗi Upload : Kênh bị đăng xuất & bị die")
            driver.quit()
            return
        
        if self.running:
            try:
                file_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="content"]/input')))
                url = f'{self.url}/{self.video["video"]}'
                filename = url.split("/")[-1]
                abs_path = os.path.abspath(os.path.join(os.getcwd(), 'Video_Upload', filename))
                file_input.send_keys(abs_path)
                self.update_signal.emit(f"Profile {data_profile['name']} Upload video thành công")
                self.update_status_video("Đang Upload :Upload video success")
            except Exception as e:
                self.update_signal.emit(e)
                self.update_signal.emit(f"Profile {data_profile['name']} không thể upload")
                self.update_status_video("Lỗi Upload : Không thể upload video")
                driver.quit()
                return

        if self.running:
            try:
                file_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="file-loader"]')))
                url = f'{self.url}/{self.video["img_thumbnail"]}'
                filename = url.split("/")[-1]
                abs_path = os.path.abspath(os.path.join(os.getcwd(), 'Video_Upload', filename))
                file_input.send_keys(abs_path)
                self.update_signal.emit(f"Profile {data_profile['name']}  Upload xong thumnail \n")
                self.update_status_video("Đang Upload :Upload thumnail success")
            except Exception as e:
                self.update_signal.emit(e)
                self.update_signal.emit(f"Profile {data_profile['name']} không thể upload \n")
                self.update_status_video("Lỗi Upload : Không thể upload thumnail")
                driver.quit()
                return
            
        if self.running:
            try:
                file_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                                    '#title-textarea > ytcp-form-input-container:nth-child(1) > div:nth-child(1) > div:nth-child(3) > div:nth-child(1) > ytcp-social-suggestion-input:nth-child(1) > div:nth-child(1)')))
                time.sleep(2)
                file_input.clear()
                file_input.clear()
                file_input.send_keys(self.video['title'])
                self.update_signal.emit(f"Profile {data_profile['name']}  Upload xong title \n")
                self.update_status_video("Đang Upload :Upload title success")
                time.sleep(2)

            except Exception as e:
                self.update_signal.emit(e)
                self.update_signal.emit(f"Profile {data_profile['name']} không thể điền \n")
                self.update_status_video("Lỗi Upload : Không thể điền title")
                driver.quit()
                return
            
        if self.running:
            try:
                file_input = wait.until(EC.element_to_be_clickable((By.XPATH,'/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-ve/ytcp-video-metadata-editor/div/ytcp-video-metadata-editor-basics/div[2]/ytcp-video-description/div/ytcp-social-suggestions-textbox/ytcp-form-input-container/div[1]/div[2]/div/ytcp-social-suggestion-input/div')))
                time.sleep(2)
                file_input.clear()
                file_input.clear()
                file_input.send_keys(self.video['description'])
                self.update_signal.emit(f"Profile {data_profile['name']}  Upload xong description \n")
                self.update_status_video("Đang Upload :Upload description success")
            except Exception as e:
                self.update_signal.emit(e)
                self.update_signal.emit(f"Profile {data_profile['name']} không thể điền \n")
                self.update_status_video("Lỗi Upload : Không thể điền description")
                driver.quit()
                return

        if self.running:
            try:
                next_button = wait.until(EC.element_to_be_clickable((By.XPATH,'/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-ve/ytcp-video-metadata-editor/div/ytcp-video-metadata-editor-basics/div[5]/ytkc-made-for-kids-select/div[4]/tp-yt-paper-radio-group/tp-yt-paper-radio-button[2]/div[1]')))
                next_button.click()

            except Exception as e:
                self.update_signal.emit(e)
                self.update_signal.emit(f"Profile {data_profile['name']} không thể click lần 1\n")
                self.update_status_video("Lỗi Upload : Không thể click next lần 1")
                driver.quit()
                return

        if self.running:
            try:
                upload_button = wait.until(EC.element_to_be_clickable((By.XPATH,"/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-ve/ytcp-video-metadata-editor/div/div/ytcp-button/div")))
                upload_button.click()
                
            except Exception as e:
                self.update_signal.emit(e)
                self.update_signal.emit(f"Profile {data_profile['name']} không thể click lần 2\n")
                self.update_status_video("Lỗi Upload : Không thể click next lần 2")
                driver.quit()
                return

        if self.running:
            try:
                file_input = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="text-input"]')))
                time.sleep(3)
                file_input.clear()
                file_input.send_keys(self.video['keykeyword'])
                self.update_signal.emit(f"Profile {data_profile['name']}  Upload xong keyworld \n")
                self.update_status_video("Đang Upload : Upload keyworld success")

            except Exception as e:
                self.update_signal.emit(f"Profile {data_profile['name']} không thể keyworld \n")
                self.update_status_video("Lỗi Upload : Không thể điền keyworld")
                driver.quit()
                return
            
        if self.running:
            try:
                next_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="next-button"]/div')))
                next_button.click()

            except Exception as e:
                self.update_signal.emit(f"Profile {data_profile['name']} không thể click lần 3\n")
                self.update_status_video("Lỗi Upload : Không thể click next lần 3")
                driver.quit()
                return
        is_money = False
        if self.running:
            try:
                next_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="text-container"]/div')))
                next_button.click()
                is_money = True
                self.update_signal.emit(f"Profile {data_profile['name']}  Upload xong quảng cáo \n")
                self.update_status_video("Đang Upload : Đang kiểm tra bật kiếm tiền")
                time.sleep(2)
            except:
                self.update_signal.emit(f"Profile {data_profile['name']} kênh này không được bật kiếm tiền\n")
                self.update_status_video("Đang Upload : Kênh này không được bật kiếm tiền")
                is_money = False
                
        if self.running and is_money:
            try:
                next_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="radio-on"]')))
                next_button.click()
                self.update_signal.emit(f"Profile {data_profile['name']}  Upload xong bật kiếm tiền \n")
                self.update_status_video("Đang Upload : Bật kiếm tiền")
                time.sleep(2)
            except Exception as e:
                self.update_signal.emit(f"Profile {data_profile['name']} không thể chọn nút kiếm tiền\n")
                self.update_status_video("Lỗi Upload : Không thể chọn nút kiếm tiền")
                driver.quit()
                return
            
            try:
                next_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="save-button"]')))
                next_button.click()
                time.sleep(10)
            except Exception as e:
                self.update_signal.emit(f"Profile {data_profile['name']} không thể lưu bật kiếm tiền\n")
                self.update_status_video("Lỗi Upload : Không thể lưu bật kiếm tiền")
                driver.quit()
                return
            
            try:
                time.sleep(2)
                next_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="place-manually-button"]/div')))
                next_button.click()
                time.sleep(2)
            except Exception as e:
                self.update_signal.emit(f"Profile {data_profile['name']} không thể chọn mở set quảng cáo\n")
                self.update_status_video("Lỗi Upload : Không thể chọn mở set quảng cáo")
                driver.quit()
                return
            
            try:
                url = self.video["video"]
                filename = f"Video_Upload/{url.split('/')[-1]}"
                with VideoFileClip(filename) as video:
                    duration = video.duration

            except Exception as e:
                duration = None
                self.update_signal.emit(f"Profile {data_profile['name']} không thể đọc thời gian video\n")
                self.update_status_video("Lỗi Upload : Không thể đọc thời gian video")
                driver.quit()
                return
            
            timestamps = self.generate_timestamps(duration)
            for timestamp in timestamps:
                try:
                    input_field = driver.find_element(By.XPATH,
                                                        '//*[@id="left-controls"]/ytcp-media-timestamp-input')
                    # Đặt con trỏ vào trường nhập liệu
                    input_field.click()
                    time.sleep(2)
                    actions = ActionChains(driver)
                    actions.key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL)  # Chọn tất cả văn bản
                    time.sleep(2)
                    actions.send_keys(Keys.DELETE)  # Xóa văn bản đã chọn
                    time.sleep(2)
                    actions.send_keys(timestamp)
                    actions.perform()
                    time.sleep(2)
                    next_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="add-ad-break"]/div')))
                    next_button.click()
                    time.sleep(1)

                except Exception as e:
                    self.update_signal.emit(f"Profile {data_profile['name']} không thể chọn đặt thời gian quảng cáo\n")
                    self.update_status_video("Lỗi Upload : Không thể chọn đặt thời gian quảng cáo")
                    driver.quit()
                    return
                
            try:
                next_button = wait.until(EC.element_to_be_clickable((By.XPATH,
                                                                     '/html/body/ytve-ad-breaks-modal/ytve-modal-host/ytcp-dialog/tp-yt-paper-dialog/div[1]/div/div[2]/div[2]/ytcp-button/div')))
                next_button.click()
                time.sleep(2)
                self.update_signal.emit(f"Profile {data_profile['name']}  Upload xong quảng cáo \n")
                self.update_status_video(data_profile, "Đang Upload :Upload quảng cáo success")
            except Exception as e:
                self.update_signal.emit(f"Profile {data_profile['name']} không thể chọn xong quảng cáo\n")
                self.update_status_video("Lỗi Upload : Không thể chọn xong quảng cáo")
                driver.quit()
                return
            
            try:
                next_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="next-button"]/div')))
                next_button.click()
                time.sleep(2)

            except Exception as e:
                self.update_signal.emit(f"Profile {data_profile['name']} không thể click lần 4\n")
                self.update_status_video("Lỗi Upload : Không thể click next lần 4")
                driver.quit()
                return
            
            try:
                # Tìm phần tử checkbox
                checkbox = driver.find_element(By.ID, "checkbox")
                # Sử dụng ActionChains để mô phỏng việc click vào checkbox
                ActionChains(driver).click(checkbox).perform()

            except Exception as e:
                self.update_signal.emit(f"Profile {data_profile['name']} không thể click checkbox\n")
                self.update_status_video("Lỗi Upload : Không thể click checkbox")
                driver.quit()
                return
            
            try:
                next_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="submit-questionnaire-button"]/div')))
                next_button.click()
                time.sleep(10)
            except Exception as e:
                self.update_signal.emit(f"Profile {data_profile['name']} không thể click lần 5\n")
                self.update_status_video("Lỗi Upload : Không thể click next lần 5")
                driver.quit()
                return

            try:
                next_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="next-button"]/div')))
                next_button.click()
                time.sleep(2)
            except Exception as e:
                self.update_signal.emit(f"Profile {data_profile['name']} không thể click lần 6\n")
                self.update_status_video("Lỗi Upload : Không thể click next lần 6")
                driver.quit()
                return
            
        if self.running:
            try:
                next_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="next-button"]/div')))
                next_button.click()
                time.sleep(2)
            except Exception as e:
                self.update_signal.emit(f"Profile {data_profile['name']} không thể click lần 7\n")
                self.update_status_video("Lỗi Upload : Không thể click next lần 7")
                driver.quit()
                return

        if self.running:
            try:
                next_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="next-button"]/div')))
                next_button.click()
                time.sleep(6)
            except Exception as e:
                self.update_signal.emit(f"Profile {data_profile['name']} không thể click lần 8\n")
                self.update_status_video("Lỗi Upload : Không thể click next lần 8")
                driver.quit()
                return
            
        if self.running:
            try:
                next_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="second-container-expand-button"]/tp-yt-iron-icon')))
                next_button.click()
                time.sleep(2)

            except Exception as e:
                self.update_signal.emit(f"Profile {data_profile['name']} không thể click lần 9\n")
                self.update_status_video("Lỗi Upload : Không thể click next lần 9")
                driver.quit()
                return
            
        if self.running:
            try:
                next_button = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="datepicker-trigger"]/ytcp-dropdown-trigger/div/div[2]/span')))
                next_button.click()
                time.sleep(2)
            except Exception as e:
                self.update_signal.emit(f"Profile {data_profile['name']} không thể click lần 10\n")
                self.update_status_video("Lỗi Upload : Không thể click next lần 10")
                driver.quit()
                return
            
        if self.running:
            try:
                next_button = wait.until(EC.element_to_be_clickable((By.XPATH,
                                                                        '/html/body/ytcp-date-picker/tp-yt-paper-dialog/div/form/tp-yt-paper-input/tp-yt-paper-input-container/div[2]/div/iron-input/input')))
                next_button.click()
                next_button.clear()
                time.sleep(2)
                date = self.convert_date_format(self.video['date_upload'])
                next_button.send_keys(date)
                next_button.send_keys(Keys.RETURN)

                self.update_signal.emit(f"Profile {data_profile['name']}  Upload xong ngày uppic \n")
                self.update_status_video("Đang Upload : Upload ngày uppic success")
                
            except Exception as e:
                self.update_signal.emit(f"Profile {data_profile['name']} không thể cài đặt ngày uppic\n")
                self.update_status_video("Lỗi Upload : Không thể cài đặt ngày uppic")
                data_profile['count_upload_today'] += 1
                driver.quit()
                return
            
        if self.running:
            try:
                time.sleep(1)
                next_button = wait.until(EC.element_to_be_clickable((By.XPATH,
                                                                        '/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-uploads-review/div[2]/div[1]/ytcp-video-visibility-select/div[3]/div[2]/ytcp-visibility-scheduler/div[1]/ytcp-datetime-picker/div/div[2]/form/ytcp-form-input-container/div[1]/div/tp-yt-paper-input/tp-yt-paper-input-container/div[2]/div/iron-input/input')))
                next_button.click()
                next_button.clear()
                time.sleep(2)
                next_button.send_keys(self.video['time_upload'])
                next_button.send_keys(Keys.RETURN)

                self.update_signal.emit(f"Profile {data_profile['name']}  Upload xong giờ uppic \n")
                self.update_status_video("Đang Upload :Upload giờ uppic success")
               
                time.sleep(2)
            except Exception as e:
                self.update_signal.emit(f"Profile {data_profile['name']} không thể cài đặt giờ uppic\n")
                self.update_status_video("Lỗi Upload : Không thể cài đặt giờ uppic")
                data_profile['count_upload_today'] += 1
                driver.quit()

                return
            
        if self.running:
            try:
                Xpath = '//*[@id="dialog"]/div/ytcp-animatable[2]/div/div[1]/ytcp-video-upload-progress/span'
                # Định nghĩa Xpath và các văn bản để kiểm tra
                locator = (By.XPATH, Xpath)
                texts = ["Upload complete", "Processing up to", "Checks complete."]
                # Sử dụng lambda để định nghĩa một expected condition tùy chỉnh
                element = WebDriverWait(driver, 800).until(
                    lambda driver: self.check_video_upload_success(driver, locator, texts)
                )
            except Exception as e:
                data_profile['count_upload_today'] += 1
                print(f"An error occurred: {e}")

        if self.running:
            try:
                next_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="done-button"]/div')))
                next_button.click()
                time.sleep(2)
            except Exception as e:
                self.update_signal.emit(f"Profile {profile['name']} không thể click lưu video\n")
                self.update_status_video("Lỗi Upload : Không thể click lưu video")
                data_profile['count_upload_today'] += 1
                driver.quit()
                return
            
        if is_money:
            try:
                next_button = wait.until(EC.element_to_be_clickable((By.XPATH,'/html/body/ytcp-prechecks-warning-dialog/ytcp-dialog/tp-yt-paper-dialog/div[3]/div/ytcp-button/div')))
                next_button.click()
                time.sleep(5)

            except Exception as e:
                self.update_signal.emit(f"Profile {data_profile['name']} không thể click lưu video\n")
                self.update_status_video("Lỗi Upload : Không thể click lưu video")
                data_profile['count_upload_today'] += 1
                driver.quit()
                return
            
        if  self.running:
            self.update_signal.emit(f"Profile {data_profile['name']} Upload video thành công\n")
            self.update_status_video("upload thành công")
            data_profile['count_upload_today'] += 1
            self.infor_video = None
            driver.quit()
    
    def generate_timestamps(self, duration_seconds, start_seconds=3, interval_seconds=150):
        timestamps = []
        current_seconds = start_seconds
        is_long_duration = duration_seconds < 3600
        while current_seconds <= duration_seconds:
            formatted_time = self.convert_seconds_to_time_format(current_seconds, is_long_duration)
            timestamps.append(formatted_time)
            current_seconds += interval_seconds
        return timestamps

    def convert_seconds_to_time_format(self, duration_seconds, is_long_duration):
        hours = int(duration_seconds // 3600)
        minutes = int((duration_seconds % 3600) // 60)
        seconds = int(duration_seconds % 60)
        frames = 00  # Giả định khung hình là 00
        if is_long_duration:
            return f"{minutes:02}:{seconds:02}:{frames:02}"
        else:
            return f"{hours:02}:{minutes:02}:{seconds:02}:{frames:02}"

    def download_video(self):
        url = f'{self.url}/{self.video["img_thumbnail"]}'
        filename = url.split("/")[-1]
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            path = os.path.join("Video_Upload", filename)
            with open(path, 'wb') as file:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, file)
            self.update_signal.emit("Download thumbnail success")

        url = f'{self.url}/{self.video["video"]}'
        filename = url.split("/")[-1]
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            path = os.path.join("Video_Upload", filename)
            with open(path, 'wb') as file:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, file)

    def check_video_upload_success(self, driver, locator, texts):
        try:
            element = driver.find_element(*locator)  # Sử dụng phương thức công khai để tìm phần tử
            element_text = element.text
            return any(text in element_text for text in texts)
        except NoSuchElementException:
            return False

    def update_status_video(self,status):
       requests.post(f"{self.url}update-status-video/",data={'id':self.video['id'],'status':status})

    def convert_date_format(self, date_str):
        # Chuyển đổi từ định dạng YYYY-MM-DD sang định dạng MMM DD, YYYY
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%b %d, %Y")
        return formatted_date

    def get_video_upload(self,id_folder,id_profile):
        url = f"{self.url}get-video-content/"
        self.update_signal.emit(f"Đang lấy thông tin {id_folder['name']} --- {id_profile['name']} ...")
        response = requests.post(url, data={'id': id_folder['id'], 'id_profile': id_profile['id']}).json()
        if response['success'] == True:
            self.video = response['video']
            self.update_signal.emit(f"Đã lấý thành công thông tin {id_folder['name']} --- {id_profile['name']} ")
            return True
        else:
            self.update_signal.emit(f"Không có video của {id_folder['name']} --- {id_profile['name']} ")
            return False

    def save_data(self):
                # Giả sử self.config chứa dữ liệu JSON của bạn
        self.config['folder'] = sorted(self.config['folder'], key=lambda x: x['id'])  # Sắp xếp các folder nếu cần

        for folder in self.config['folder']:
            folder['profiles'] = sorted(folder['profiles'], key=lambda x: x['id'])  # Sắp xếp các profile trong mỗi folder

        # Tiếp tục ghi lại dữ liệu vào tệp như trước
        with open("config.json", "w", encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)
    
    def stop(self):
       self.running = False

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

class MyApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        self.uic = Ui_MainWindow()
        self.uic.setupUi(self)
        self.setWindowTitle('App Upload')
        self.show()
        self.config = self.load_data()
        self.show_data()
        self.is_start = False
        self.url = self.uic.lineEdit.text()
        self.uic.pushButton_2.clicked.connect(self.button_add_profile)
        self.uic.pushButton_6.clicked.connect(self.button_save_url)
        self.uic.pushButton_3.clicked.connect(self.button_delete_profile)
        self.uic.pushButton_5.clicked.connect(self.button_open_profile)
        self.uic.pushButton_4.clicked.connect(self.button_setting_profile)
        self.uic.pushButton.clicked.connect(self.button_start_upload)

    def button_add_profile(self):
        if self.uic.lineEdit.text():
            input_text_dialog = From_add_profile(self.url,self.config)
            result = input_text_dialog.exec()
            if result == QDialog.DialogCode.Accepted:
                self.config = input_text_dialog.config
                self.save_data()
                self.show_data()
        else:
            QMessageBox.warning(self, 'Warning', 'Please enter the URL')

    def button_save_url(self):
        if self.uic.lineEdit.text():
            self.config['url'] = self.uic.lineEdit.text()
            self.save_data()
            self.url = self.uic.lineEdit.text()

            QMessageBox.warning(self, 'Success', 'Save URL Success')
        else:
            QMessageBox.warning(self, 'Warning', 'Please enter the URL')

    def button_delete_profile(self):
        selected = self.uic.listWidget.currentItem()
        if selected is not None:
            text = selected.text()
            folder_name, profile_name = text.split(' --- ')
            for forder in self.config['folder']:
                if forder['name'] == folder_name:
                    for profile in forder['profiles']:
                        if profile['name'] == profile_name:
                            forder['profiles'].remove(profile)
                            self.save_data()
                            self.show_data()
                            break
            QMessageBox.warning(self, 'Warning', 'Please select a profile to delete.')
        else:
            QMessageBox.warning(self, 'Warning', 'vui lòng chọn profile để xóa.')
    
    def button_open_profile(self):
        selected = self.uic.listWidget.currentItem()
        if selected is not None:
            text = selected.text()
            folder_name, profile_name = text.split(' --- ')
            for forder in self.config['folder']:
                if forder['name'] == folder_name:
                    for profile in forder['profiles']:
                        if profile['name'] == profile_name:
                            self.open_profile(profile['path_profile'])
                            break
                        
                           
        else:
            QMessageBox.warning(self, 'Warning', 'vui lòng chọn profile để mở.')

    def button_setting_profile(self):
        selected = self.uic.listWidget.currentItem()
        if selected is not None:
            input_text_dialog = From_setting_profile(selected.text(),self.config)
            result = input_text_dialog.exec()
            if result == QDialog.DialogCode.Accepted:
                self.config = input_text_dialog.config
                self.save_data()
                self.show_data()
        else:
            QMessageBox.warning(self, 'Warning', 'vui lòng chọn profile cài đặt')

    def open_profile(self,path):
        try:
            options = Options()
            profile = FirefoxProfile(profile_directory=rf"{path}")
            options.add_argument("--start-maximized")
            options.profile = profile
            driver = webdriver.Firefox(options=options)
            driver.get("https://www.youtube.com/")
        except Exception as e:
            QMessageBox.warning(self, 'Warning', 'Sai đường dẫn link vui lòng cập nhập lại đường link profile')
    
    def button_start_upload(self):
        if self.is_start == False:
            self.is_start = True
            self.uic.pushButton.setText('Stop')
            self.update_status_app('Start upload')
            self.uic.pushButton.setStyleSheet("background-color: red")
            self.uic.lineEdit.setDisabled(True)
            self.uic.pushButton_2.setDisabled(True)
            self.uic.pushButton_3.setDisabled(True)
            self.uic.pushButton_4.setDisabled(True)
            self.uic.pushButton_5.setDisabled(True)
            self.uic.pushButton_6.setDisabled(True)
            self.thread = ServerThread()
            self.thread.update_signal.connect(self.update_status_app)
            self.thread.start()

        else:
            self.is_start = False
            self.uic.pushButton.setText('Start')
            self.update_status_app('Stop upload')
            self.uic.pushButton.setStyleSheet("background-color: rgb(85, 170, 0)")
            self.uic.lineEdit.setDisabled(False)
            self.uic.pushButton_2.setDisabled(False)
            self.uic.pushButton_3.setDisabled(False)
            self.uic.pushButton_4.setDisabled(False)
            self.uic.pushButton_5.setDisabled(False)
            self.uic.pushButton_6.setDisabled(False)
            self.config = self.load_data()
            self.thread.stop()

    def update_status_app(self,text):
        tz = pytz.timezone('Asia/Ho_Chi_Minh')
        current_time = datetime.now(tz)
        formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
        self.uic.plainTextEdit.insertPlainText(f"{formatted_time} : {text}\n")  # Thêm dòng log mới
        scrollbar = self.uic.plainTextEdit.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def load_data(self):
        if not os.path.exists("config.json"):
            config = {
                'url': 'http://88.99.198.189:8000/',
                'folder': []
            }
            with open("config.json", "w", encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
        else:
            with open("config.json", "r",encoding='utf-8') as f:
                config = json.load(f)
        return config  # Return the loaded or default configuration
    
    def save_data(self):
                # Giả sử self.config chứa dữ liệu JSON của bạn
        self.config['folder'] = sorted(self.config['folder'], key=lambda x: x['id'])  # Sắp xếp các folder nếu cần

        for folder in self.config['folder']:
            folder['profiles'] = sorted(folder['profiles'], key=lambda x: x['id'])  # Sắp xếp các profile trong mỗi folder

        # Tiếp tục ghi lại dữ liệu vào tệp như trước
        with open("config.json", "w", encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)

    def show_data(self):
        self.uic.listWidget.clear()
        self.uic.lineEdit.setText(self.config['url'])
        for item in self.config['folder']:
            for profile in item['profiles']:
                text = f"{item['name']} --- {profile['name']}"
                self.uic.listWidget.addItem(text)


if __name__ == '__main__':
    app = QApplication([])
    window = MyApplication()
    app.exec()




