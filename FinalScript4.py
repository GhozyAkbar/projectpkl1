import csv
import subprocess
import os

# Fungsi untuk mendownload konten dari website menggunakan wget dan mengecek status code
def download_website_content(url):
    try:
        # Menggunakan wget dengan opsi --spider untuk mengecek status code terlebih dahulu
        wget_check_command = [
            "wget", 
            "--spider",  # Cek status tanpa mendownload konten
            "--server-response",  # Menampilkan header HTTP dari server
            "--max-redirect=20",  # Mengikuti hingga 20 pengalihan
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0", 
            url
        ]
        result = subprocess.run(wget_check_command, capture_output=True, text=True)
        output = result.stderr  # wget menulis informasi ke stderr

        # Mencari status code dalam output wget
        status_code = None
        for line in output.splitlines():
            if "HTTP/" in line:
                status_code = int(line.split()[1])  # Ambil status code

        if status_code != 200:
            print(f"Skipping {url}: Status code {status_code}")
            return None, status_code  # Skip jika status code bukan 200
        
        # Jika status code 200, lanjutkan mendownload halaman
        wget_download_command = [
            "wget", 
            "--quiet", 
            "--max-redirect=20", 
            "--content-on-error", 
            "--output-document=temp.html", 
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0", 
            url
        ]
        subprocess.run(wget_download_command, check=True)
        print(f"Konten dari {url} berhasil diunduh.")
        return True, status_code  # Berhasil download dan status code 200
    except subprocess.CalledProcessError as e:
        print(f"Gagal mengunduh konten dari {url}: {e}")
        return None, None

# Fungsi untuk memfilter konten berdasarkan wordlist judi online
def filter_content_with_grep():
    # Membuka file wordlist.txt
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
        urls.append(f"http://{row[0]}")  # Menambahkan http:// di depan URL

# Menyimpan hasil ke dalam CSV baru
output_file_path = "scan_results.csv"

with open(output_file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Domain", "Status Code", "Gambling Content"])  # Menulis header CSV
    
    # Mengecek status code dan mendownload konten dari setiap URL
    for url in urls:
        success, status_code = download_website_content(url)
        
        if success:  # Jika konten berhasil diunduh dan status code 200
            # Memeriksa ukuran file
            if os.path.getsize('temp.html') < 10000:  # Ukuran minimal file
                print(f"Skipping {url}: Page is empty or too small.")
                os.remove('temp.html')  # Menghapus file jika terlalu kecil
                writer.writerow([url, status_code, "Skipped (Page too small)"])
                continue  # Lanjut ke URL berikutnya

            # Memfilter konten berdasarkan kata kunci judi
            has_gambling_content = filter_content_with_grep()
            
            # Menambahkan hasil deteksi ke file CSV
            writer.writerow([url, status_code, "Yes" if has_gambling_content else "No"])
        else:
            writer.writerow([url, status_code, "Skipped"])

        # Pastikan file temp.html dihapus setelah selesai digunakan
        if os.path.exists('temp.html'):
            os.remove('temp.html')

print(f"Hasil pemindaian telah disimpan ke {output_file_path}")
