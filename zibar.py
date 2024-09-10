from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# Data login
username = "aliefyan.hidayah@student.poltekssn.ac.id"
password = "JarKom20*"

# Fungsi untuk melakukan login otomatis ke Any.Run
def login_anyrun(driver, url):
    driver.get("https://httpstatus.io/")

    try:
        url_input_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[2]/section[1]/div/form/div[1]/div/p[1]/textarea"))
        )
        url_input_field.send_keys(url)

    except Exception as e:
        print(f"Error processing {url}: {e}")
        return False


# Fungsi untuk submit URL ke AnyRun setelah login
def submit_url_to_anyrun(driver, url):
    try:
        # Tunggu tombol "New Task" untuk submit URL dan klik
        new_task_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[3]/div/div/div/div/div/div/div[1]/div/div[2]/div[1]"))
        )
        new_task_button.click()

        # Tunggu form input URL muncul
        url_input_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[4]/div[2]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[3]/div/input"))
        )
        url_input_field.send_keys(url) #peer nya disini ygy

        # Klik tombol submit atau start analisis
        start_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[4]/div[2]/div/div/div[1]/div[2]/div/div[3]/button"))
        )
        start_button.click()

        # Tunggu hasil analisis ditampilkan (ini memakan waktu)
        print("Waiting for analysis to complete...")
        time.sleep(60)  # Menunggu selama 60 detik atau lebih untuk proses analisis selesai

        # Ambil teks hasil analisis
        analysis_result = driver.find_element(By.TAG_NAME, 'body').text.lower()

        # Kata kunci yang berhubungan dengan situs judi online
        gambling_keywords = ['zeus', 'bet', 'poker', 'slot', 'gamble', 'jackpot', 'sportsbook']
        
        for keyword in gambling_keywords:
            if keyword in analysis_result:
                print(f"The URL {url} is classified as a gambling site.")
                return True
        
        print(f"The URL {url} is NOT classified as a gambling site.")
        return False

    except Exception as e:
        print(f"Error processing {url}: {e}")
        return False

def main():
    # Setup driver menggunakan Chrome
    service = ChromeService(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    try:
        # Login ke AnyRun
        if login_anyrun(driver):
            # Daftar URL yang terindikasi sebagai web judi online
            urls = [
                'slot-mahjong.pa-talu.go.id'
            ]

            for url in urls:
                submit_url_to_anyrun(driver, url)
                time.sleep(100)  # Tunggu beberapa saat sebelum melanjutkan ke URL berikutnya
        else:
            print("Login failed. Unable to proceed with URL submission.")

    finally:
        # Tutup browser setelah selesai
        driver.quit()

if __name__ == '__main__':
    main()

