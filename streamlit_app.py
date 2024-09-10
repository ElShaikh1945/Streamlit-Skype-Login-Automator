import os
import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import threading
import time

def extract_credentials(file):
    credentials = []
    content = file.read().decode("utf-8")
    lines = content.split("\n")
    for line in lines:
        if line.strip():
            email, password = line.strip().split(':')
            credentials.append((email, password))
    return credentials

class SkypeLogin:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.driver = self.start_tor_browser()

    def get_tor_browser_path(self):
        """
        Tries to detect the Tor Browser installation path for common systems.
        """
        possible_paths = [
            r"C:\Program Files\Tor Browser\Browser\firefox.exe",
            r"C:\Program Files (x86)\Tor Browser\Browser\firefox.exe",
            r"C:\Users\%USERNAME%\AppData\Local\Tor Browser\Browser\firefox.exe".format(os.getlogin()),
            "/usr/bin/tor-browser",
            "/usr/local/bin/tor-browser",
            "/Applications/Tor Browser.app/Contents/MacOS/firefox"
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        raise Exception("Tor Browser executable not found. Please ensure it's installed and add the path manually.")

    def start_tor_browser(self):
        tor_path = self.get_tor_browser_path()
        options = webdriver.FirefoxOptions()
        options.binary_location = tor_path
        driver = webdriver.Firefox(options=options)
        return driver

    def login(self):
        self.driver.get("https://login.live.com/login.srf?wa=wsignin1.0&rpsnv=157&ct=1722705703&rver=7.5.2156.0&wp=MBI_SSL...")
        
        try:
            WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable((By.ID, "i0116"))).send_keys(self.email)
        except TimeoutException:
            st.write("TimeoutException occurred. Retrying...")
            self.login()

        self.driver.find_element(By.ID, "idSIButton9").click()

        try:
            password_field = WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable((By.ID, "i0118")))
            password_field.send_keys(self.password)
            password_field.send_keys(u'\ue007')

            time.sleep(5)

            try:
                self.driver.find_element(By.XPATH, "//button[contains(text(), 'Yes')]").click()
            except:
                st.write(f"Could not find 'Yes' button for account {self.email}. Closing window.")
                self.driver.quit()
                return

            try:
                WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Verify your account')]")))
                st.write(f"Account {self.email} needs verification. Closing window.")
                self.driver.quit()
                return
            except:
                pass
        except TimeoutException:
            st.write("TimeoutException occurred. Retrying...")
            self.login()

        st.write(f"Successfully logged in to Skype with {self.email}")
        self.driver.quit()

def login_thread(skype_login):
    skype_login.login()

st.title("Skype Login Automation using Tor")

uploaded_file = st.file_uploader("Upload credentials file (format: email:password)", type="txt")

if uploaded_file:
    credentials = extract_credentials(uploaded_file)
    for email, password in credentials:
        st.write(f"Logging in to Skype with {email}...")
        skype_login = SkypeLogin(email, password)
        threading.Thread(target=login_thread, args=(skype_login,)).start()
