from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import requests

##LOGIN FUNCTION##
# Data login
username = "aliefyan.hidayah@student.poltekssn.ac.id"
password = "JarKom20*"

# Fungsi untuk melakukan login otomatis ke Any.Run
def login_anyrun():
    ##URL DEFINITION##
    csv_file_path = "dummy_urls.csv"
    urls = []
    with open(csv_file_path, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Melewati header
        for row in reader:
            urls.append(row[0])

    # Pastikan chromedriver terpasang dan dapat diakses
    driver = webdriver.Chrome()  # Pastikan path ChromeDriver sesuai
    driver.get("https://app.any.run/")

    try:
        # Tunggu halaman utama dimuat
        time.sleep(3)

        # Pilih menu "Sign In" menggunakan Xpath yang diberikan
        sign_in_button = driver.find_element(By.XPATH, "/html/body/div[1]/div[4]/div[2]/div/div/div[1]/div[2]/div/div/div[2]/div[1]/label[2]")
        sign_in_button.click()

        # Tunggu hingga form login muncul dengan WebDriverWait (maks 10 detik)
        wait = WebDriverWait(driver, 10)

        # Tunggu field email untuk terlihat dan aktif, kemudian masukkan username
        email_field = wait.until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/div[4]/div[2]/div/div/div[1]/div[2]/div/div/div[2]/div[2]/form/div[1]/div[1]/input")))
        email_field.send_keys(username)

        # Tunggu field password untuk terlihat dan aktif, kemudian masukkan password
        password_field = wait.until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/div[4]/div[2]/div/div/div[1]/div[2]/div/div/div[2]/div[2]/form/div[2]/div[1]/input")))
        password_field.send_keys(password)

        # Tunggu tombol login terlihat, lalu klik
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[4]/div[2]/div/div/div[1]/div[2]/div/div/div[2]/div[2]/form/div[3]/button[1]")))
        login_button.click()

        # Tunggu beberapa saat untuk memastikan login berhasil
        time.sleep(5)

        # Tambahkan logika setelah login, seperti memverifikasi URL atau dashboard halaman
        print("Login successful!")

    except Exception as e:
        print(f"Login failed: {str(e)}")

    finally:
        # Jangan lupa tutup browser setelah selesai
        driver.quit()

if __name__ == "__main__":

    login_anyrun()
