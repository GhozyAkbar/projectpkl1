import csv
import subprocess
import os
import sys

# Fungsi untuk mendownload konten dari website menggunakan wget dan mengecek status code
def download_website_content(url):
    try:
        # Menggunakan wget dengan opsi --spider untuk mengecek status code terlebih dahulu
        wget_check_command = [
            "wget", 
            "--spider",  # Cek status tanpa mendownload konten
            "--server-response",  # Menampilkan header HTTP dari server
            "--max-redirect=20",  # Mengikuti hingga 20 pengalihan
            "--timeout=5",
            "--tries=1",
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
            "--timeout=5",
            "--tries=1", 
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0", 
            url
        ]
        subprocess.run(wget_download_command, check=True)
        print(f"Konten dari {url} berhasil diunduh.")
        return True, status_code  # Berhasil download dan status code 200
    except subprocess.CalledProcessError as e:
        print(f"Gagal mengunduh konten dari {url}: {e}")
        return None, None

# Fungsi untuk memfilter konten berdasarkan kata "exclude" dan kata kunci dari wordlist
def filter_content_with_grep():
    # Membuka file exclude.txt
    with open('exclude.txt', 'r') as exclude_file:
        exclude_keywords = [word.strip() for line in exclude_file for word in line.strip().split()]

    # Mengecek apakah ada kata exclude dalam konten
    for exclude_keyword in exclude_keywords:
        try:
            grep_exclude_command = ["grep", "-i", exclude_keyword, "temp.html"]
            result = subprocess.run(grep_exclude_command, capture_output=True, text=True)
            if result.stdout:
                print(f"Kata exclude '{exclude_keyword}' ditemukan. Melewati URL ini.")
                return "exclude"  # Jika kata exclude ditemukan, hentikan proses dan skip URL
        except subprocess.CalledProcessError as e:
            print(f"Error saat menjalankan grep untuk exclude keyword {exclude_keyword}: {e}")

    # Membuka file wordlist.txt jika tidak ada kata exclude
    with open('wordlist.txt', 'r') as wordlist_file:
        gambling_keywords = [word.strip() for line in wordlist_file for word in line.strip().split()]

    # Cek apakah ada kata kunci perjudian dalam konten
    for keyword in gambling_keywords:
        try:
            grep_command = ["grep", "-i", keyword, "temp.html"]
            result = subprocess.run(grep_command, capture_output=True, text=True)
            if result.stdout:
                print(f"Ditemukan kata kunci '{keyword}' di dalam konten.")
                return True
        except subprocess.CalledProcessError as e:
            print(f"Error saat menjalankan grep untuk keyword {keyword}: {e}")
    
    return False

# csv_file_path = "7ud0l.csv"
csv_file_path = sys.argv[1]

urls = []
with open(csv_file_path, mode='r') as file:
    reader = csv.reader(file, delimiter=';')  # Menentukan pemisah sebagai semicolon
    next(reader)  # Melewati header jika ada
    for row in reader:
        urls.append(row[0])

# Menyimpan hasil ke dalam CSV baru
output_file_path = "scan_results.csv"

with open(output_file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Domain", "Status Code", "Gambling Content"])  # Menulis header CSV
    
    # Mengecek status code dan mendownload konten dari setiap URL
    for url in urls:
        success, status_code = download_website_content(url)
        
        if success:  # Jika konten berhasil diunduh dan status code 200

            # Memfilter konten berdasarkan kata exclude dan kata kunci perjudian
            result = filter_content_with_grep()
            if result == "exclude":
                writer.writerow([url, status_code, "Skipped (Exclude Found)"])
            else:
                writer.writerow([url, status_code, "Yes" if result else "No"])
        else:
            writer.writerow([url, status_code, "Skipped"])

        # Pastikan file temp.html dihapus setelah selesai digunakan
        if os.path.exists('temp.html'):
            os.remove('temp.html')

print(f"Hasil pemindaian telah disimpan ke {output_file_path}")
