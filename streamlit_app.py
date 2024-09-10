import streamlit as st
import threading
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import io

def extract_credentials(file):
    credentials = []
    for line in file:
        email, password = line.decode("utf-8").strip().split(':')
        credentials.append((email, password))
    return credentials

class SkypeLogin:
    def __init__(self, email, password):
        options = webdriver.ChromeOptions()
        options.add_argument("--incognito")
        self.driver = webdriver.Chrome(options=options)
        self.email = email
        self.password = password

    def login(self):
        self.driver.get("https://login.live.com/login.srf?wa=wsignin1.0&rpsnv=157&ct=1722705703&rver=7.5.2156.0&wp=MBI_SSL&wreply=https%3A%2F%2Flw.skype.com%2Flogin%2Foauth%2Fproxy%3Fclient_id%3D572381%26redirect_uri%3Dhttps%253A%252F%252Fweb.skype.com%252FAuth%252FPostHandler%253FopenPstnPage%253Dtrue%26state%3Dcf0424c2-a3d7-486c-8c09-49cfa05f6bb1&lc=1033&id=293290&mkt=en-US&psi=skype&lw=1&cobrandid=2befc4b5-19e3-46e8-8347-77317a16a5a5&client_flight=ReservedFlight33%2CReservedFlight67")
        try:
            WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.ID, "i0116"))).send_keys(self.email)
        except TimeoutException:
            st.write("TimeoutException occurred. Retrying...")
            self.login()
        self.driver.find_element(By.ID, "idSIButton9").click()
        try:
            password_field = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.ID, "i0118")))
            password_field.send_keys(self.password)
            password_field.send_keys(u'\ue007')  # Send the Enter key
            time.sleep(2)  # Wait for the "Yes" button to appear
            try:
                self.driver.find_element(By.XPATH, "//button[contains(text(), 'Yes')]").click()  # Click the "Yes" button
            except:
                st.write(f"Could not find 'Yes' button for account {self.email}. Closing window.")
                self.driver.quit()  # Close the window
    
            try:
                verify_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Verify your account')]")))
                st.write(f"Account {self.email} needs verification. Closing window.")
                self.driver.quit()  # Close the window
                return
            except:
                pass
        except TimeoutException:
            st.write("TimeoutException occurred. Retrying...")
            self.login()

skype_logins = []

def login_thread(skype_login):
    skype_login.login()
    skype_logins.append(skype_login)

def start_login_process(file):
    credentials = extract_credentials(file)
    for email, password in credentials:
        st.write(f"Logging in to Skype with {email}...")
        skype_login = SkypeLogin(email, password)
        threading.Thread(target=login_thread, args=(skype_login,)).start()

def main():
    st.title("Skype Login Automation")
    file = st.file_uploader("Upload a file with credentials", type=["txt"])
    if file is not None:
        start_login_process(file)

if __name__ == "__main__":
    main()
