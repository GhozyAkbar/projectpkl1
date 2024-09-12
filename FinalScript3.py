import csv
import requests
import subprocess
import os  # Tambahan untuk mengakses fungsi os.path.getsize dan os.remove

# Fungsi untuk mengecek response code suatu URL
def check_url_status(url):
    try:
        # Mengirim request GET ke URL
        response = requests.get(url, timeout=10)  # Timeout untuk menghindari waktu tunggu terlalu lama
        return response.status_code
    except requests.exceptions.RequestException as e:
        # Jika ada error saat mengakses URL, tampilkan error
        print(f"Error saat mengakses {url}: {e}")
        return None

# Fungsi untuk mendownload konten dari website menggunakan wget
def download_website_content(url):
    try:
        # Menggunakan wget untuk mendownload halaman web ke file temp.html
        wget_command = ["wget", "-q", "-O", "temp.html", url]
        subprocess.run(wget_command, check=True)
        print(f"Konten dari {url} berhasil diunduh.")
    except subprocess.CalledProcessError as e:
        print(f"Gagal mengunduh konten dari {url}: {e}")

# Fungsi untuk memfilter konten berdasarkan wordlist judi online
def filter_content_with_grep():
    # Membuka file wordlist.txt menggunakan context manager
    with open('wordlist.txt', 'r') as file:
        gambling_keywords = [word.strip() for line in file for word in line.strip().split()]

    # Buat command grep untuk mencari kata kunci di file temp.html
    for keyword in gambling_keywords:
        try:
            grep_command = ["grep", "-i", keyword, "temp.html"]
            result = subprocess.run(grep_command, capture_output=True, text=True)
            if result.stdout:
                print(f"Ditemukan kata kunci '{keyword}' di dalam konten.")
                return True  # Jika ditemukan salah satu kata kunci, langsung return True
        except subprocess.CalledProcessError as e:
            print(f"Error saat menjalankan grep untuk keyword {keyword}: {e}")
    return False  # Tidak ada kata kunci yang ditemukan

# Baca URL dari file CSV yang dipisahkan dengan semicolon (;)
csv_file_path = "7ud0l.csv"

urls = []
with open(csv_file_path, mode='r') as file:
    reader = csv.reader(file, delimiter=';')  # Menentukan pemisah sebagai semicolon
    next(reader)  # Melewati header jika ada
    for row in reader:
        # Menambahkan http:// di depan URL
        urls.append(f"http://{row[0]}")
        urls.append(f"https://{row[0]}")
# Menyimpan hasil ke dalam CSV baru
output_file_path = "scan_results.csv"

with open(output_file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Domain", "Status Code", "Gambling Content"])  # Menulis header CSV
    
    # Mengecek status code dari setiap URL dan menyimpan hasilnya
    for url in urls:
        status_code = check_url_status(url)
        if status_code:
            if status_code == 200:  # Jika status code 200, coba download konten dan cek
                download_website_content(url)
                
                # Memeriksa ukuran file
                if os.path.getsize('temp.html') < 8000:  # Ukuran minimal file
                    print(f"Skipping {url}: Page is empty or too small.")
                    os.remove('temp.html')  # Menghapus file jika terlalu kecil
                    writer.writerow([url, status_code, "Skipped (Page too small)"])
                    continue  # Lanjut ke URL berikutnya
                
                has_gambling_content = filter_content_with_grep()
                
                # Tambahkan hasil deteksi ke file CSV
                writer.writerow([url, status_code, "Yes" if has_gambling_content else "No"])
            else:
                writer.writerow([url, status_code, "Skipped"])
        else:
            print(f"URL: {url} - Gagal mendapatkan status code.")

        # Pastikan file temp.html dihapus setelah selesai digunakan
        if os.path.exists('temp.html'):
            os.remove('temp.html')

print(f"Hasil pemindaian telah disimpan ke {output_file_path}")
