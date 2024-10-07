import requests
import json
import time

# URL untuk scraping
scrape_url = "https://worm.birds.dog/worms/me?page=1&perPage=100"
# Template untuk URL listing dan unlisting
listing_url_template = "https://worm.birds.dog/worms/listing/{id}"
unlisting_url_template = "https://worm.birds.dog/worms/delist/{id}"

# Fungsi untuk membaca Authorization dari file auth.txt
def read_auth_token():
    try:
        with open('auth.txt', 'r') as f:
            return f.read().strip()
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

# Fungsi untuk menangani delay saat rate limit tercapai
def handle_rate_limit(response):
    retry_after = 60  # Default ke 60 detik
    print(f"Rate limit exceeded. Retrying in {retry_after} seconds...")
    time.sleep(retry_after)

# Scraping data
def scrape():
    response = requests.get(scrape_url, headers=headers)
    if response.status_code == 200:
        print("Scraping berhasil!")
        data = response.json()
        save_data(data)
    else:
        print("Terjadi kesalahan saat scraping:", response.status_code, response.text)
        handle_rate_limit(response)

# Listing data yang status minted
def list_items():
    scrape()  # Lakukan scraping sebelum listing
    data = load_data()
    minted_items = [item for item in data if item.get('status') == 'minted']
    print("Daftar Item yang Statusnya Minted:")

    prices = {}
    item_types = set(item['type'] for item in minted_items)

    print("Mengumpulkan harga untuk setiap tipe item...")
    for item_type in item_types:
        price = float(input(f"Masukkan harga untuk tipe {item_type.capitalize()}: "))
        prices[item_type] = price

    for item in minted_items:
        listing_url = listing_url_template.format(id=item['id'])
        payload = {"price": prices[item['type']]}
        response = requests.post(listing_url, headers=headers, json=payload)

        if response.status_code == 200:
            print(f"Item {item['type']} (UID: {item['uid']}) berhasil dilisting dengan harga {prices[item['type']]}.")
        else:
            print(f"Gagal listing item {item['type']} (UID: {item['uid']}): {response.status_code} - {response.text}")
            if response.status_code == 429:
                handle_rate_limit(response)

        time.sleep(1)

# Unlisting data yang status listed
def unlist_items():
    scrape()  # Lakukan scraping sebelum unlisting
    data = load_data()
    listed_items = [item for item in data if item.get('status') == 'listed']
    print("Daftar Item yang Statusnya Listed:")

    for item in listed_items:
        unlisting_url = unlisting_url_template.format(id=item['id'])
        payload = {}
        response = requests.post(unlisting_url, headers=headers, json=payload)

        if response.status_code == 200:
            print(f"Item {item['type']} (UID: {item['uid']}) berhasil diunlist.")
        else:
            print(f"Gagal unlisting item {item['type']} (UID: {item['uid']}): {response.status_code} - {response.text}")
            if response.status_code == 429:
                handle_rate_limit(response)

        time.sleep(1)

# List semua lalu unlist semua dan ulangi setiap 5 menit
def list_then_unlist_all():
    while True:
        print("Proses listing semua item unlisted...")
        list_items()  # List semua item yang unlisted

        print("Menunggu 1 menit sebelum meng-unlist semua item yang listed...")
        time.sleep(60)  # Tunggu 1 menit sebelum melakukan unlisting

        print("Proses unlisting semua item listed...")
        unlist_items()  # Unlist semua item yang listed

        print("Menunggu 5 menit untuk mengulang proses...")
        time.sleep(300)  # Tunggu 5 menit sebelum mengulang proses

# Fungsi utama untuk menjalankan proses
def main():
    print("1. List Items")
    print("2. Unlist Items")
    print("3. List Semua, kemudian Unlist Semua Listed")

    choice = input("Pilih opsi (1/2/3): ")

    if choice == '1':
        list_items()
    elif choice == '2':
        unlist_items()
    elif choice == '3':
        list_then_unlist_all()
    else:
        print("Pilihan tidak valid.")

# Panggil fungsi utama
if __name__ == "__main__":
    main()
