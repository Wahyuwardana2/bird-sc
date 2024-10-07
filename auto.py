import requests
import json
import time  # Untuk menambahkan delay

# URL untuk scraping
scrape_url = "https://worm.birds.dog/worms/me?page=1&perPage=100"
# Template untuk URL listing dan unlisting
listing_url_template = "https://worm.birds.dog/worms/listing/{id}"
unlisting_url_template = "https://worm.birds.dog/worms/delist/{id}"

# Fungsi untuk membaca Authorization dari file auth.txt
def read_auth_token():
    try:
        with open('auth.txt', 'r') as f:
            return f.read().strip()  # Baca file dan hapus karakter newline/whitespace
    except FileNotFoundError:
        print("File auth.txt tidak ditemukan!")
        return None

# Membaca Authorization token
auth_token = read_auth_token()

# Cek apakah Authorization token valid
if not auth_token:
    print("Authorization token tidak valid, hentikan proses.")
    exit()

# Header yang diperlukan, diambil dari file auth.txt
headers = {
    "Authorization": auth_token,
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
}

# Menyimpan data hasil scraping
def save_data(data):
    with open('scraped_data.json', 'w') as f:
        json.dump(data, f)

# Mengambil data yang sudah disimpan
def load_data():
    try:
        with open('scraped_data.json', 'r') as f:
            return json.load(f)['data']  # Ambil hanya bagian 'data'
    except (FileNotFoundError, json.JSONDecodeError):
        return []  # Kembalikan list kosong jika tidak ada data yang valid

# Scraping data
def scrape():
    response = requests.get(scrape_url, headers=headers)
    if response.status_code == 200:
        print("Scraping berhasil!")
        data = response.json()
        # Simpan/update data
        save_data(data)
    else:
        print("Terjadi kesalahan saat scraping:", response.status_code, response.text)

# Fungsi untuk memasukkan harga di awal
def input_prices():
    prices = {}
    item_types = ["common", "rare", "epic", "legend", "mythic"]

    print("Masukkan harga untuk setiap tipe item:")
    for item_type in item_types:
        price = float(input(f"Masukkan harga untuk tipe {item_type.capitalize()}: "))
        prices[item_type] = price

    return prices

# Proses listing dan unlisting
def process_items(prices):
    scrape()  # Lakukan scraping sebelum memproses item
    data = load_data()
    
    # Unlisting items yang statusnya listed
    listed_items = [item for item in data if item.get('status') == 'listed']
    unlisted_count = 0
    for item in listed_items:
        unlisting_url = unlisting_url_template.format(id=item['id'])
        payload = {}  # Body kosong
        response = requests.post(unlisting_url, headers=headers, json=payload)

        time.sleep(1)  # Delay 1 detik sebelum melakukan permintaan berikutnya

        if response.status_code == 200:
            print(f"Item {item['type']} (UID: {item['uid']}) berhasil diunlist.")
            unlisted_count += 1
            # Langsung listing kembali setelah unlisting
            listing_url = listing_url_template.format(id=item['id'])
            price = prices.get(item['type'], 2500)  # Ambil harga dari input awal
            listing_payload = {"price": price}
            listing_response = requests.post(listing_url, headers=headers, json=listing_payload)

            time.sleep(1)  # Delay 1 detik sebelum listing

            if listing_response.status_code == 200:
                print(f"Item {item['type']} (UID: {item['uid']}) berhasil dilisting kembali dengan harga {price}.")
            else:
                print(f"Gagal listing item {item['type']} (UID: {item['uid']}): {listing_response.status_code} - {listing_response.text}")
        elif response.status_code == 429:
            print("Rate limit exceeded. Menunggu 70 detik sebelum melanjutkan...")
            time.sleep(70)  # Delay 70 detik jika rate limit exceeded
            continue  # Lanjutkan ke item berikutnya
        else:
            print(f"Gagal unlisting item {item['type']} (UID: {item['uid']}): {response.status_code} - {response.text}")

        # Batasi jumlah unlisting dan listing ke 15 ID
        if unlisted_count >= 15:
            print("Mencapai batas 15 ID, menunggu 65 detik sebelum melanjutkan...")
            time.sleep(65)  # Tunggu 65 detik sebelum melanjutkan
            unlisted_count = 0  # Reset penghitung

# Fungsi utama untuk menjalankan proses
def main():
    # Input harga di awal
    prices = input_prices()

    while True:  # Loop tak terbatas
        print("Memulai proses scraping, unlisting, dan listing...")
        process_items(prices)
        print("Semua item telah diproses. Menunggu 5 menit sebelum memulai ulang...")
        time.sleep(300)  # Tunggu 5 menit sebelum memulai ulang proses

# Panggil fungsi utama
if __name__ == "__main__":
    main()
