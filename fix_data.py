import pandas as pd
import numpy as np
import random

# File Input & Output
INPUT_TRAFFIC = 'traffic_data_history.csv'
OUTPUT_WEATHER = 'weather_data_history.csv'

def generate_perfect_weather():
    print("🔨 Sedang menjahit data cuaca agar pas dengan traffic...")
    
    try:
        # 1. Baca Data Traffic
        df_t = pd.read_csv(INPUT_TRAFFIC)
        df_t['timestamp'] = pd.to_datetime(df_t['timestamp'])
        
        # Bulatkan ke jam terdekat (agar match dengan weather)
        df_t['hour_rounded'] = df_t['timestamp'].dt.round('h')
        
        # 2. Kelompokkan per jam & lokasi (Cari rata-rata speednya)
        # Kita butuh 1 data cuaca untuk setiap (Lokasi + Jam) unik
        slots = df_t.groupby(['location_name', 'hour_rounded'])['speed_kmh'].mean().reset_index()
        
        weather_data = []

        # 3. Generate Data Cuaca Pintar
        for index, row in slots.iterrows():
            loc = row['location_name']
            time_val = row['hour_rounded']
            avg_speed = row['speed_kmh']
            
            # --- LOGIKA SIMULASI CERDAS ---
            # Tujuannya: Bikin korelasi "Hujan = Macet" jadi nyata.
            
            kode_cuaca = 3 # Default: Berawan (Code 3)
            
            # Jika Speed lambat (< 22 km/h), kita set kemungkinan besar sedang Hujan
            if avg_speed < 22: 
                if random.random() > 0.2: # 80% chance hujan kalo macet
                    kode_cuaca = 63 # Hujan Sedang (Code > 50)
                else:
                    kode_cuaca = 3
            
            # Jika Speed sedang (22 - 35 km/h), random
            elif avg_speed < 35:
                if random.random() > 0.8: # 20% chance hujan
                    kode_cuaca = 80 # Hujan Deras
            
            # Jika Speed kencang (> 35 km/h), pasti Cerah
            else:
                kode_cuaca = 1 # Cerah
                    
            weather_data.append({
                "nama_lokasi": loc,
                "waktu": time_val.strftime('%Y-%m-%dT%H:%M'), # Format ISO
                "suhu_c": round(random.uniform(24, 32), 1),
                "kode_cuaca": kode_cuaca,
                "kecepatan_angin_kmh": round(random.uniform(2, 10), 1),
                "arah_angin": random.randint(0, 360)
            })

        # 4. Simpan ke CSV
        df_w = pd.DataFrame(weather_data)
        df_w.to_csv(OUTPUT_WEATHER, index=False)
        
        print(f"✅ SUKSES! {len(df_w)} baris data cuaca berhasil digenerate.")
        print(f"📁 Disimpan ke: {OUTPUT_WEATHER}")
        print("➡️  Sekarang coba refresh web aplikasimu!")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate_perfect_weather()