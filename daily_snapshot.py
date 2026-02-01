import requests
import pandas as pd
from datetime import datetime
import pytz 
import os # Tambahan import os

# ==========================================
# 1. KONFIGURASI 5 LOKASI
# ==========================================
LOCATIONS = {
    "President University":   {"lat": -6.285500, "lon": 107.171100},
    "Terminal Cikarang":      {"lat": -6.261902, "lon": 107.137911},
    "Stasiun Cikarang":       {"lat": -6.253611, "lon": 107.142222},
    "Sentra Grosir Cikarang": {"lat": -6.258627, "lon": 107.146280},
    "Lippo Mall Cikarang":    {"lat": -6.334081, "lon": 107.136950}
}

# Nama file statis (agar history terkumpul di satu file)
CSV_FILENAME = "weather_data_history.csv"

# ==========================================
# 2. FUNGSI AMBIL DATA HARIAN (FULL DAY)
# ==========================================
def fetch_today_history(nama_lokasi, lat, lon):
    print(f"   ⏳ Mengambil data: {nama_lokasi}...", end=" ")
    
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,weathercode,windspeed_10m,winddirection_10m",
        "timezone": "Asia/Jakarta",
        "forecast_days": 1 
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        hourly = data['hourly']
        timestamps = hourly['time']
        temps = hourly['temperature_2m']
        codes = hourly['weathercode']
        winds = hourly['windspeed_10m']
        dirs = hourly['winddirection_10m']

        current_time_str = datetime.now(pytz.timezone('Asia/Jakarta')).strftime("%Y-%m-%dT%H:%M")
        
        hasil_filter = []
        
        for i in range(len(timestamps)):
            waktu_data = timestamps[i]
            
            # Stop jika waktu data sudah melewati waktu sekarang
            if waktu_data > current_time_str:
                break 
                
            hasil_filter.append({
                "nama_lokasi": nama_lokasi,
                "waktu": waktu_data,
                "suhu_c": temps[i],
                "kode_cuaca": codes[i],
                "kecepatan_angin_kmh": winds[i],
                "arah_angin": dirs[i]
            })
            
        print(f"✅ OK ({len(hasil_filter)} baris data)")
        return hasil_filter

    except Exception as e:
        print(f"❌ Error: {e}")
        return []

# ==========================================
# 3. PROGRAM UTAMA
# ==========================================
if __name__ == "__main__":
    print(f"--- 📅 DAILY WEATHER HISTORY MANAGER 📅 ---")
    print(f"Target File: {CSV_FILENAME}")
    
    # 1. Cek data lama untuk MENCEGAH DUPLIKAT
    # Karena API mengambil data dari jam 00:00, kita harus tahu data mana yang sudah punya.
    existing_records = set()
    
    if os.path.exists(CSV_FILENAME):
        try:
            df_existing = pd.read_csv(CSV_FILENAME)
            # Kita buat 'kunci unik' gabungan Lokasi + Waktu
            for index, row in df_existing.iterrows():
                key = f"{row['nama_lokasi']}_{row['waktu']}"
                existing_records.add(key)
            print(f"📄 File ditemukan. Memuat {len(existing_records)} data history lama.")
        except Exception as e:
            print(f"⚠️ Gagal membaca file lama: {e}")
    else:
        print("✨ File belum ada. Akan membuat file baru.")

    # 2. Ambil Data Baru
    all_new_data = []
    print("\n--- Mulai Mengambil Data Baru ---")
    for nama, coords in LOCATIONS.items():
        lokasi_data = fetch_today_history(nama, coords['lat'], coords['lon'])
        
        # Filter: Hanya masukkan jika data tersebut BELUM ADA di file lama
        for item in lokasi_data:
            key = f"{item['nama_lokasi']}_{item['waktu']}"
            if key not in existing_records:
                all_new_data.append(item)

    # 3. Simpan (Append) ke CSV
    if all_new_data:
        df_new = pd.DataFrame(all_new_data)
        
        # Jika file belum ada, tulis header. Jika sudah ada, jangan tulis header.
        header_mode = not os.path.exists(CSV_FILENAME)
        
        # Mode 'a' = Append (Menambahkan ke bawah)
        df_new.to_csv(CSV_FILENAME, mode='a', header=header_mode, index=False)
        
        print(f"\n🎉 SUKSES! {len(all_new_data)} data BARU ditambahkan ke '{CSV_FILENAME}'")
    else:
        print("\n✅ Data sudah up-to-date. Tidak ada data baru untuk ditambahkan.")