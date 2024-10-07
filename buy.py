import requests
import time

# Fungsi untuk mendapatkan URL berdasarkan tipe
def get_check_price_url(worm_type):
    if worm_type == "alltype":
        return "https://worm.birds.dog/markets?page=1&perPage=2&orderBy=price:lowest&is_owned=false"
    else:
        return f"https://worm.birds.dog/markets?page=1&perPage=20&orderBy=price:lowest&type={worm_type}&is_owned=false"

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

# Fungsi untuk memeriksa harga
def check_price(check_price_url):
    response = requests.get(check_price_url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        # Cek apakah ada data yang bisa diambil
        if 'data' in data and len(data['data']) > 0:
            # Ambil harga dan ID dari data
            price_gross = data['data'][0]['priceGross']  # Mengambil harga kotor
            item_id = data['data'][0]['id']               # Mengambil ID
            worm_type = data['data'][0]['wormType']       # Mengambil tipe worm
            return price_gross, item_id, worm_type
        else:
            print("No data found in response.")
            return None, None, None
    else:
        print("Error fetching price:", response.status_code)
        return None, None, None

# Fungsi untuk membeli
def buy(item_id, price):
    buy_url = f"https://worm.birds.dog/markets/buy/{item_id}"
    payload = {
        "currentPrice": price
    }
    response = requests.post(buy_url, headers=headers, json=payload)
    if response.status_code == 200:
        print("Purchase successful:", response.json())
        return True  # Mengembalikan True jika pembelian berhasil
    else:
        print("Error during purchase:", response.status_code, response.text)
        return False  # Mengembalikan False jika pembelian gagal

# Menampilkan pilihan untuk tipe worm
print("Pilih tipe worm:")
print("1. Common")
print("2. Rare")
print("3. Epic")
print("4. Legend")
print("5. Mythic")
print("6. All Types")

# Meminta input tipe worm dalam bentuk angka
try:
    worm_choice = int(input("Masukkan pilihan Anda (1-6): "))
    if worm_choice == 1:
        worm_type = "common"
    elif worm_choice == 2:
        worm_type = "rare"
    elif worm_choice == 3:
        worm_type = "epic"
    elif worm_choice == 4:
        worm_type = "legend"
    elif worm_choice == 5:
        worm_type = "mythic"
    elif worm_choice == 6:
        worm_type = "alltype"
    else:
        print("Pilihan tidak valid.")
        exit()
except ValueError:
    print("Input tidak valid, mohon masukkan angka.")
    exit()

# Meminta input dari pengguna untuk batas harga dan mengalikannya dengan 1 miliar
try:
    max_price_input = int(input(f"Masukkan batas harga maksimal untuk {worm_type} (misalnya 500: "))
    max_price = max_price_input * 1000000000  # Mengubah 500 menjadi 500.000.000.000
except ValueError:
    print("Input tidak valid, mohon masukkan angka.")
    exit()

# Loop untuk memantau harga
while True:
    check_price_url = get_check_price_url(worm_type)
    price_gross, item_id, fetched_worm_type = check_price(check_price_url)
    if price_gross is not None and item_id is not None:
        print(f"Current Gross Price: {price_gross} | Worm Type: {fetched_worm_type}")
        # Cek apakah harga kotor kurang dari batas yang diinput
        if price_gross < max_price:
            if buy(item_id, price_gross):  # Melakukan pembelian berdasarkan ID
                time.sleep(5)  # Delay 5 detik setelah pembelian berhasil
    else:
        print("Retrying after an error...")

    # Tanpa delay, akan langsung memeriksa harga lagi
