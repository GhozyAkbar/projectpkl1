import csv
import subprocess
import os
import sys

def download_website_content(url):
    try:
        wget_check_command = [
            "wget", 
            "--spider",  # Cek status tanpa mendownload konten
            "--server-response",  # Menampilkan header HTTP dari server
            "--max-redirect=20",  # Mengikuti hingga 20 pengalihan
            "--timeout=5",  # timeout precess 5 seconds
            "--tries=1",  # try connect 1 time 
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0", 
            url
        ]
        result = subprocess.run(wget_check_command, capture_output=True, text=True)
        output = result.stderr

        status_code = None
        for line in output.splitlines():
            if "HTTP/" in line:
                status_code = int(line.split()[1])

        if status_code != 200:
            print(f"Skipping {url}: Status code {status_code}")
            return None, status_code

        wget_download_command = [
            "wget", 
            "--quiet", 
            "--max-redirect=20", 
            "--content-on-error", #  download content although error status code
            "--output-document=temp.html",
            "--timeout=5",
            "--tries=1", 
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0", 
            url
        ]
        subprocess.run(wget_download_command, check=True)
        print(f"Konten dari {url} berhasil diunduh.")
        return True, status_code
    except subprocess.CalledProcessError as e:
        print(f"Gagal mengunduh konten dari {url}: {e}")
        return None, None

def filter_content_with_grep():
    with open('offjudol.txt', 'r') as exclude_file:
        exclude_keywords = [word.strip() for line in exclude_file for word in line.strip().split()]

    for exclude_keyword in exclude_keywords:
        try:
            grep_exclude_command = ["grep", "-i", exclude_keyword, "temp.html"]
            result = subprocess.run(grep_exclude_command, capture_output=True, text=True)
            if result.stdout:
                print(f"Kata exclude '{exclude_keyword}' ditemukan. Melewati URL ini.")
                return "exclude"
        except subprocess.CalledProcessError as e:
            print(f"Error saat menjalankan grep untuk exclude keyword {exclude_keyword}: {e}")

    with open('onjudol.txt', 'r') as wordlist_file:
        gambling_keywords = [word.strip() for line in wordlist_file for word in line.strip().split()]

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

csv_file_path = sys.argv[1]

urls = []
with open(csv_file_path, mode='r') as file:
    reader = csv.reader(file, delimiter=';')
    next(reader)
    for row in reader:
        urls.append(row[0])

output_file_path = "scan_results.csv"

with open(output_file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Domain", "Judol Content"])

    for url in urls:
        success, status_code = download_website_content(url)

        if success:

            result = filter_content_with_grep()
            if result == "exclude":
                writer.writerow([url, "Skipped (No Judol Content)"])
            else:
                writer.writerow([url, "Yes" if result else "No"])
        else:
            writer.writerow([url, "Skipped (Status Code Not 200)"])

        if os.path.exists('temp.html'):
            os.remove('temp.html')

print(f"Hasil pemindaian telah disimpan ke {output_file_path}")
