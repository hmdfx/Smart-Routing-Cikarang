import requests
import pandas as pd
from datetime import datetime
import pytz # Library untuk zona waktu (pip install pytz)

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

# ==========================================
# 2. FUNGSI AMBIL DATA HARIAN (FULL DAY)
# ==========================================
def fetch_today_history(nama_lokasi, lat, lon):
    print(f"   ⏳ Mengambil data: {nama_lokasi}...", end=" ")
    
    # URL untuk meminta data per jam (Hourly)
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,weathercode,windspeed_10m,winddirection_10m",
        "timezone": "Asia/Jakarta", # Pastikan pakai WIB
        "forecast_days": 1 # Hanya minta data hari ini
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        # Data dari API berupa list panjang (00:00 - 23:00)
        hourly = data['hourly']
        timestamps = hourly['time']
        temps = hourly['temperature_2m']
        codes = hourly['weathercode']
        winds = hourly['windspeed_10m']
        dirs = hourly['winddirection_10m']

        # Kita harus filter: Ambil hanya yang waktunya <= Sekarang
        current_time_str = datetime.now(pytz.timezone('Asia/Jakarta')).strftime("%Y-%m-%dT%H:%M")
        
        hasil_filter = []
        
        for i in range(len(timestamps)):
            waktu_data = timestamps[i]
            
            # LOGIKA UTAMA: Stop jika waktu data sudah melewati waktu sekarang
            if waktu_data > current_time_str:
                break 
                
            # Masukkan ke list
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
    print("--- 📅 DAILY WEATHER SNAPSHOT (00:00 - NOW) 📅 ---")
    today_str = datetime.now().strftime("%Y-%m-%d")
    output_file = f"weather_data.csv"
    
    all_data = []

    # Loop 5 Lokasi
    for nama, coords in LOCATIONS.items():
        lokasi_data = fetch_today_history(nama, coords['lat'], coords['lon'])
        all_data.extend(lokasi_data)

    # Simpan ke CSV
    if all_data:
        df = pd.DataFrame(all_data)
        df.to_csv(output_file, index=False)
        print(f"\n🎉 SUKSES! {len(all_data)} data tersimpan di '{output_file}'")
        print("Silakan buka file CSV untuk melihat data dari jam 00:00 sampai sekarang.")
    else:
        print("\n⚠️ Tidak ada data yang tersimpan.")