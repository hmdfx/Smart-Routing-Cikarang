import requests
import csv
import time
import os
from datetime import datetime

# ================= KONFIGURASI =================
TOMTOM_API_KEY = "icrWu22nNRnduwbKTU1ClF2oiVWGZCYl"

# Daftar 5 Lokasi Cikarang
LOCATIONS = [
    {'nama': 'Terminal Cikarang',      'lat': '-6.2619', 'lon': '107.1379'},
    {'nama': 'Sentra Grosir Cikarang', 'lat': '-6.2584', 'lon': '107.1462'},
    {'nama': 'Stasiun Cikarang',       'lat': '-6.2536', 'lon': '107.1422'},
    {'nama': 'Lippo Mall Cikarang',    'lat': '-6.3341', 'lon': '107.1369'},
    {'nama': 'President University',   'lat': '-6.2850', 'lon': '107.1706'}
]

# Agar File CSV tersimpan di folder yang sama dengan script (Anti Error)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILENAME = os.path.join(SCRIPT_DIR, "traffic_data.csv")

def get_speed(lat, lon):
    """Hanya mengambil data kecepatan (km/h)"""
    url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?key={TOMTOM_API_KEY}&point={lat},{lon}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json().get('flowSegmentData', {})
            return data.get('currentSpeed') # Mengembalikan nilai integer, misal: 45
    except Exception as e:
        print(f"Error koneksi: {e}")
    return None

def main():
    print("=== MONITORING SPEED CIKARANG (5 LOKASI) ===")
    print(f"Menyimpan data ke: {CSV_FILENAME}")
    print("Tekan CTRL+C untuk berhenti.\n")

    headers = ['timestamp', 'location_name', 'speed_kmh']

    # Cek file, jika belum ada buat header
    if not os.path.exists(CSV_FILENAME):
        with open(CSV_FILENAME, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()

    try:
        while True:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] Mengambil data kecepatan...")

            with open(CSV_FILENAME, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                
                for loc in LOCATIONS:
                    speed = get_speed(loc['lat'], loc['lon'])
                    
                    if speed is not None:
                        writer.writerow({
                            'timestamp': timestamp,
                            'location_name': loc['nama'],
                            'speed_kmh': speed
                        })
                        print(f"   > {loc['nama']}: {speed} km/h")
                    else:
                        print(f"   > {loc['nama']}: Gagal mengambil data")
            
            print("   --- Jeda 1 menit ---\n")
            time.sleep(60) # Ambil data setiap 60 detik

    except KeyboardInterrupt:
        print("\nProgram dihentikan.")

if __name__ == "__main__":
    main()