import os
import subprocess
import re

# Path ke file yang berisi daftar link temuan judi online
link_list_path = '7ud0l.csv'
# Path ke wordlist yang berkaitan dengan judi online
wordlist_path = 'wordlist.txt'
# Output hasil temuan valid
output_path = 'hasil_validasi_judi.txt'

# Membaca daftar link judi
with open(link_list_path, 'r') as f:
    links = f.read().splitlines()

# Membaca wordlist yang berhubungan dengan judi online
with open(wordlist_path, 'r') as f:
    wordlist = f.read().splitlines()

# Fungsi untuk menjalankan wget pada suatu link dan menyimpan hasilnya
def download_website(link):
    try:
        # Menjalankan perintah wget dengan user-agent yang ditentukan
        subprocess.run(f'wget --user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0" -O temp_website.html {link}', shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

# Fungsi untuk mencocokkan konten website dengan wordlist
def check_for_gambling_content():
    with open('temp_website.html', 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        found_words = []
        # Mencari setiap kata dalam wordlist di konten website
        for word in wordlist:
            if re.search(rf'\b{word}\b', content, re.IGNORECASE):
                found_words.append(word)
        return found_words

# Membuat atau membersihkan file hasil output
with open(output_path, 'w') as output_file:
    output_file.write("Hasil Validasi Link Judi Online\n")
    output_file.write("=" * 50 + "\n\n")

# Proses validasi
for link in links:
    print(f"Memeriksa {link}...")
    if download_website(link):
        found_words = check_for_gambling_content()
        if found_words:
            # Menyimpan hasil validasi jika ada kata yang ditemukan
            with open(output_path, 'a') as output_file:
                output_file.write(f"Link: {link}\n")
                output_file.write(f"Temuan: {', '.join(found_words)}\n")
                output_file.write(f"Bukti: Konten website mengandung kata-kata terkait judi: {', '.join(found_words)}\n")
                output_file.write("-" * 50 + "\n\n")
    else:
        print(f"Gagal mengunduh {link}.")

# Menghapus file sementara
if os.path.exists('temp_website.html'):
    os.remove('temp_website.html')

print("Proses validasi selesai. Hasil disimpan di", output_path)