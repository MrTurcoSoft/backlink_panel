# app/comment_bot.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import os

def post_comment(url, name="Max Mustermann", email="max@example.com", comment="Toller Artikel! Mehr Infos: https://www.airstyler-alternative.de"):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        time.sleep(3)

        textarea = driver.find_element(By.TAG_NAME, "textarea")
        textarea.send_keys(comment)

        name_input = driver.find_element(By.NAME, "author")
        name_input.send_keys(name)

        email_input = driver.find_element(By.NAME, "email")
        email_input.send_keys(email)

        submit_buttons = driver.find_elements(By.XPATH, "//input[@type='submit'] | //button[@type='submit']")
        if submit_buttons:
            submit_buttons[0].click()
            time.sleep(2)

            os.makedirs("screenshots", exist_ok=True)
            screenshot_path = f"screenshots/{int(time.time())}.png"
            driver.save_screenshot(screenshot_path)
            return True, screenshot_path
        else:
            return False, None

    except Exception as e:
        return False, None

    finally:
        driver.quit()
