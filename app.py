from flask import Flask, render_template, jsonify
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)

# --- KONFIGURASI FILE ---
# Pastikan path file sesuai dengan lokasi file di komputer kamu
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRAFFIC_CSV = os.path.join(BASE_DIR, 'traffic_data.csv') # Sesuaikan nama file traffic kamu
WEATHER_CSV = os.path.join(BASE_DIR, 'weather_data.csv')   # File weather kamu

# Lokasi Koordinat
LOCATIONS = {
    'Terminal Cikarang':      {'lat': -6.2619, 'lon': 107.1379},
    'Sentra Grosir Cikarang': {'lat': -6.2584, 'lon': 107.1462},
    'Stasiun Cikarang':       {'lat': -6.2536, 'lon': 107.1422},
    'Lippo Mall Cikarang':    {'lat': -6.3341, 'lon': 107.1369},
    'President University':   {'lat': -6.2850, 'lon': 107.1706}
}

def get_latest_traffic(location_name):
    """Membaca data traffic terakhir"""
    if not os.path.exists(TRAFFIC_CSV): return None
    try:
        df = pd.read_csv(TRAFFIC_CSV)
        loc_data = df[df['location_name'] == location_name]
        if not loc_data.empty: return loc_data.iloc[-1]
    except: pass
    return None

def get_current_weather(location_name):
    """Membaca data weather berdasarkan JAM SAAT INI"""
    if not os.path.exists(WEATHER_CSV): return None
    try:
        df = pd.read_csv(WEATHER_CSV)
        
        # 1. Filter Lokasi
        df_loc = df[df['nama_lokasi'] == location_name].copy()
        
        # 2. Cari data yang jam-nya paling dekat dengan sekarang
        now_hour = datetime.now().strftime('%Y-%m-%dT%H') # Format: 2026-01-25T22
        
        # Kita cari string yang mengandung jam sekarang
        # (Karena format di CSV kamu: 2026-01-25T22:00)
        matched_row = df_loc[df_loc['waktu'].str.contains(now_hour, na=False)]
        
        if not matched_row.empty:
            return matched_row.iloc[0]
        else:
            # Jika jam sekarang belum ada (misal update telat), ambil data paling akhir
            if not df_loc.empty:
                return df_loc.iloc[-1]
                
    except Exception as e:
        print(f"Error Weather: {e}")
    return None

@app.route('/')
def index():
    return render_template('index.html', locations=LOCATIONS.keys())

@app.route('/api/get_conditions/<start_loc>/<end_loc>')
def get_conditions(start_loc, end_loc):
    data = {
        "start": {"speed": 0, "rain": 0, "temp": 0, "weather_code": 0},
        "end":   {"speed": 0, "rain": 0, "temp": 0, "weather_code": 0}
    }

    # --- 1. AMBIL TRAFFIC (Speed) ---
    t_start = get_latest_traffic(start_loc)
    t_end = get_latest_traffic(end_loc)
    
    # Pastikan nama kolom sesuai CSV Traffic kamu (misal: 'speed_kmh' atau 'current_speed')
    if t_start is not None: data["start"]["speed"] = int(t_start.get('speed_kmh', 0))
    if t_end is not None:   data["end"]["speed"]   = int(t_end.get('speed_kmh', 0))

    # --- 2. AMBIL WEATHER (Suhu & Kode Cuaca) ---
    w_start = get_current_weather(start_loc)
    w_end = get_current_weather(end_loc)

    # MAPPING KOLOM SESUAI CSV WEATHER KAMU:
    # nama_lokasi, waktu, suhu_c, kode_cuaca, kecepatan_angin_kmh, arah_angin
    
    if w_start is not None:
        data["start"]["temp"] = float(w_start['suhu_c'])
        data["start"]["weather_code"] = int(w_start['kode_cuaca'])
        # Karena tidak ada kolom hujan, kita prediksi dari kode cuaca
        # Kode > 50 biasanya berarti hujan/gerimis di WMO code
        code = int(w_start['kode_cuaca'])
        data["start"]["rain"] = 5.0 if code >= 50 else 0.0 

    if w_end is not None:
        data["end"]["temp"] = float(w_end['suhu_c'])
        data["end"]["weather_code"] = int(w_end['kode_cuaca'])
        code = int(w_end['kode_cuaca'])
        data["end"]["rain"] = 5.0 if code >= 50 else 0.0

    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)