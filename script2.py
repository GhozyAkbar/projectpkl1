import csv
import os
import subprocess

# Nama file CSV dan wordlist
csv_file = 'urls.csv'
wordlist_file = 'wordlist_judi.txt'
output_file = 'valid_urls.txt'

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

def validate_urls_from_csv(csv_file):
    valid_urls = []

    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        header = next(reader)  # Assuming first row is the header
        url_index = header.index('URL')  # Ubah ini sesuai dengan nama kolom URL di CSV

        for row in reader:
            url = row[url_index]
            print(f"Checking {url}")
            if is_valid_judi_site(url):
                valid_urls.append(url)

    return valid_urls

# Eksekusi proses validasi URL
valid_urls = validate_urls_from_csv(csv_file)

# Simpan hasil valid URL ke dalam file
with open(output_file, 'w') as file:
    for url in valid_urls:
        file.write(url + '\n')

print(f"Valid URLs saved to {output_file}")
