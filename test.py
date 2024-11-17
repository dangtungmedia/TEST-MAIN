from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Initialize the WebDriver (use Chrome in this example)
driver = webdriver.Chrome()

# Open YouTube or any website
driver.get("https://www.youtube.com")
time.sleep(5)  # Wait for the page to load fully

# Get cookies after login
cookies = driver.get_cookies()
print("Extracted Cookies:", cookies)

# Save cookies to a file (optional)
with open("youtube_cookies.txt", "w") as file:
    for cookie in cookies:
        file.write(f"{cookie['name']}={cookie['value']}; domain={cookie['domain']}; path={cookie['path']}\n")

# Close the browser
driver.quit()
