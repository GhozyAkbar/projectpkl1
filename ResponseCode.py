import csv
import requests

# Fungsi untuk mengecek response code suatu URL
def check_url_status(url):
    try:
        # Mengirim request GET ke URL
        response = requests.get(url, timeout=10)  # Timeout untuk menghindari waktu tunggu terlalu lama
        
        # Mengembalikan kode status dari response
        return response.status_code
    except requests.exceptions.RequestException as e:
        # Jika ada error saat mengakses URL, tampilkan error
        print(f"Error saat mengakses {url}: {e}")
        return None

# Baca URL dari file CSV yang telah dibuat sebelumnya
csv_file_path = "dummy_urls.csv"

urls = []
with open(csv_file_path, mode='r') as file:
    reader = csv.reader(file)
    next(reader)  # Melewati header
    for row in reader:
        urls.append(row[0])

# Menyimpan hasil ke dalam CSV baru
output_file_path = "scan_results.csv"

with open(output_file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Domain", "Status Code"])  # Menulis header CSV
    
    # Mengecek status code dari setiap URL dan menyimpan hasilnya
    for url in urls:
        status_code = check_url_status(url)
        if status_code:
            writer.writerow([url, status_code])
        else:
            print(f"URL: {url} - Gagal mendapatkan status code.")

print(f"Hasil pemindaian telah disimpan ke {output_file_path}")
