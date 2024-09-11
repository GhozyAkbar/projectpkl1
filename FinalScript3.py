import csv
import requests
import subprocess
import os

# Wordlist kata kunci yang berhubungan dengan situs judi online
wordlist_file = 'wordlist.txt'
a = open(wordlist_file, 'r')
b = a.readlines()
gambling_keywords = []
for line in b:
    for item in line.strip().split():
        gambling_keywords.append(item)

def is_valid_judi_site(url):
    try:
        # Download halaman menggunakan wget, hanya download jika status kode HTTP adalah 200
        wget_command = f"wget --spider --server-response {url} 2>&1 | grep 'HTTP/' | tail -1 | grep '200'"
        result = subprocess.run(wget_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Jika status kode HTTP bukan 200, skip URL ini
        if result.returncode != 0:
            print(f"Skipping {url}: Not a valid page or returned error status.")
            return False

        # Download halaman untuk pemeriksaan lebih lanjut
        os.system(f"wget -q -O temp_page.html {url}")

        # Periksa ukuran file untuk memastikan halaman tidak kosong
        if os.path.getsize('temp_page.html') < 50000:  # Misalnya, ukuran file minimal 100 byte
            print(f"Skipping {url}: Page is empty or too small.")
            os.remove('temp_page.html')
            return False
        
        # Cek apakah halaman mengandung kata dari wordlist judi online
        grep_command = f"grep -i -f {wordlist_file} temp_page.html"
        result = subprocess.run(grep_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Jika tidak ada hasil dari grep, berarti bukan situs judi online
        if not result.stdout:
            print(f"Skipping {url}: No gambling keywords found.")
            os.remove('temp_page.html')
            return False

        # Periksa elemen frontend yang umum di situs judi (misalnya ada elemen game, banner, dll.)
        with open('temp_page.html', 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Misalnya periksa keberadaan elemen spesifik seperti <div> dengan class yang umum di situs judi
        if '<div' not in content or '<img' not in content:  # Ini hanya contoh, sesuaikan dengan elemen yang dicari
            print(f"Skipping {url}: No relevant frontend elements found.")
            os.remove('temp_page.html')
            return False

        # Jika semua pemeriksaan lolos, maka situs dianggap valid sebagai situs judi online
        os.remove('temp_page.html')
        return True

    except Exception as e:
        print(f"Error processing {url}: {e}")
    
    return False

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

# Fungsi untuk mendownload konten dari website menggunakan wget
def download_website_content(url):
    try:
        # Menggunakan wget untuk mendownload halaman web ke file temp.html
        wget_command = ["wget", "-O", "temp.html", url]
        subprocess.run(wget_command, check=True)
        print(f"Konten dari {url} berhasil diunduh.")
    except subprocess.CalledProcessError as e:
        print(f"Gagal mengunduh konten dari {url}: {e}")

# Fungsi untuk memfilter konten berdasarkan wordlist judi online
def filter_content_with_grep():

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

# Fungsi untuk memastikan URL memiliki skema
def ensure_url_scheme(url):
    if not url.startswith(('http://', 'https://')):
        return f"http://{url}"
    return url

# Fungsi utama (main)
def main():
    csv_target = "7ud0l.csv"
    urls = []

    # Baca URL dari file CSV yang dipisahkan dengan semicolon (;)
    with open(csv_target, mode='r') as file:
        reader = csv.reader(file, delimiter=';')  # Menentukan pemisah sebagai semicolon
        next(reader)  # Melewati header jika ada
        for row in reader:
            full_url = ensure_url_scheme(row[0])  # Pastikan URL memiliki skema (http atau https)
            urls.append(full_url)

    # Menyimpan hasil ke dalam CSV baru
    output_file_path = "scan_results.csv"
    with open(output_file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Domain", "Status Code", "Gambling Content"])  # Menulis header CSV
        
        # Mengecek status code dari setiap URL dan menyimpan hasilnya
        for url in urls:
            # status_code = check_url_status(url)
            # if status_code:
            #     if status_code == 200:  # Jika status code 200, coba download konten dan cek
            #         download_website_content(url)
            #         has_gambling_content = filter_content_with_grep()

            #         # Tambahkan hasil deteksi ke file CSV
            #         writer.writerow([url, status_code, "Yes" if has_gambling_content else "No"])
            #     else:
            #         writer.writerow([url, status_code, "Skipped"])

            is_valid_judi_site(url)

            # else:
            #     print(f"URL: {url} - Gagal mendapatkan status code.")

    print(f"Hasil pemindaian telah disimpan ke {output_file_path}")

# Jalankan fungsi main jika file ini dieksekusi
if __name__ == "__main__":
    main()
