from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
import time
from dotenv import load_dotenv
import os
import gmail

load_dotenv()
LINKEDIN_LOGIN = os.getenv("LINKEDIN_LOGIN")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")
chrome_driver_path = 'webdriver/chromedriver.exe'


class LinkHandling:
    def __init__(self, links):
        self.links = links
        self.to_remove = []
        self.driver = webdriver.Chrome(chrome_driver_path)

    def login_to_linkedin(self):
        for data in self.links:
            msg_id = data["id"]
            link = data["link"]
            wait = WebDriverWait(self.driver, 2)
            self.driver.get(link)
            self.driver.find_element(By.XPATH, '/html/body/header/nav/div/a[2]').click()
            login = self.driver.find_element(By.ID, "username")
            password = self.driver.find_element(By.ID, "password")
            login.send_keys(LINKEDIN_LOGIN)
            password.send_keys(LINKEDIN_PASSWORD)
            self.driver.find_element(By.XPATH, '//*[@id="organic-div"]/form/div[3]/button').click()
            try:
                verification_window = wait.until(EC.element_to_be_clickable((By.ID, 'input__email_verification_pin')))
            except TimeoutException:
                pass
            else:
                time.sleep(2)
                ver_bot = gmail.GmailBot()
                ver_bot.credentials()
                ver_pin = ver_bot.search_for_verification(3)
                verification_window.send_keys(ver_pin)
                self.driver.find_element(By.XPATH, '//*[@id="email-pin-submit-button"]').click()
            finally:
                time.sleep(1)
                self.driver.find_element(By.CSS_SELECTOR, "[class*='react-button__trigger']").click()
                print("Post liked.")
                time.sleep(1)
                self.driver.quit()
                self.to_remove.append(msg_id)
        return self.to_remove
