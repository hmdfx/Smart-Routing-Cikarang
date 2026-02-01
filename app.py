from flask import Flask, render_template, jsonify
import pandas as pd
import numpy as np
import os
from datetime import datetime

app = Flask(__name__)

# ================= KONFIGURASI FILE =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# KITA HANYA PAKAI 2 FILE INI UNTUK SEMUA FITUR
# Pastikan nama file ini sesuai dengan yang kamu upload
TRAFFIC_BIG_DATA = os.path.join(BASE_DIR, 'traffic_data_history.csv')
WEATHER_BIG_DATA = os.path.join(BASE_DIR, 'weather_data_history.csv')

# Lokasi Koordinat
LOCATIONS = {
    'Terminal Cikarang':      {'lat': -6.2619, 'lon': 107.1379},
    'Sentra Grosir Cikarang': {'lat': -6.2584, 'lon': 107.1462},
    'Stasiun Cikarang':       {'lat': -6.2536, 'lon': 107.1422},
    'Lippo Mall Cikarang':    {'lat': -6.3341, 'lon': 107.1369},
    'President University':   {'lat': -6.2850, 'lon': 107.1706}
}

# ================= HELPER FUNCTIONS =================

def get_latest_traffic(location_name):
    """Mengambil data PALING BARU dari file Big Data"""
    if not os.path.exists(TRAFFIC_BIG_DATA): return None
    try:
        # Baca Big Data
        df = pd.read_csv(TRAFFIC_BIG_DATA)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Filter lokasi
        loc_data = df[df['location_name'] == location_name]
        
        if not loc_data.empty:
            # Urutkan dari yang paling baru, ambil 1 teratas
            latest = loc_data.sort_values(by='timestamp', ascending=False).iloc[0]
            return latest
    except Exception as e:
        print(f"Error Traffic: {e}")
    return None

def get_current_weather(location_name):
    """Mengambil data weather PALING BARU dari file Big Data"""
    if not os.path.exists(WEATHER_BIG_DATA): return None
    try:
        df = pd.read_csv(WEATHER_BIG_DATA)
        # Sesuaikan nama kolom waktu (waktu / timestamp)
        df['waktu'] = pd.to_datetime(df['waktu']) 
        
        df_loc = df[df['nama_lokasi'] == location_name]
        
        if not df_loc.empty:
            # Ambil data paling akhir (paling baru)
            latest = df_loc.sort_values(by='waktu', ascending=False).iloc[0]
            return latest
    except Exception as e:
        print(f"Error Weather: {e}")
    return None

# ================= ROUTES =================

@app.route('/')
def index():
    return render_template('index.html', locations=LOCATIONS.keys())

@app.route('/api/get_conditions/<start_loc>/<end_loc>')
def get_conditions(start_loc, end_loc):
    """API Realtime: Mengambil data terakhir dari History"""
    data = {
        "start": {"speed": 0, "rain": 0, "temp": 0, "weather_code": 0},
        "end":   {"speed": 0, "rain": 0, "temp": 0, "weather_code": 0}
    }

    # 1. AMBIL SPEED TERAKHIR
    t_start = get_latest_traffic(start_loc)
    t_end = get_latest_traffic(end_loc)
    
    if t_start is not None: data["start"]["speed"] = int(t_start.get('speed_kmh', 0))
    if t_end is not None:   data["end"]["speed"]   = int(t_end.get('speed_kmh', 0))

    # 2. AMBIL CUACA TERAKHIR
    w_start = get_current_weather(start_loc)
    w_end = get_current_weather(end_loc)
    
    if w_start is not None:
        data["start"]["temp"] = float(w_start['suhu_c'])
        data["start"]["weather_code"] = int(w_start['kode_cuaca'])
        data["start"]["rain"] = 5.0 if int(w_start['kode_cuaca']) >= 50 else 0.0 

    if w_end is not None:
        data["end"]["temp"] = float(w_end['suhu_c'])
        data["end"]["weather_code"] = int(w_end['kode_cuaca'])
        data["end"]["rain"] = 5.0 if int(w_end['kode_cuaca']) >= 50 else 0.0

    return jsonify(data)

@app.route('/api/analytics/<location_name>')
def get_analytics(location_name):
    """API Analytics: Mengolah seluruh data Big Data"""
    print(f"\n--- ANALYTICS: {location_name} ---")
    try:
        if not os.path.exists(TRAFFIC_BIG_DATA):
            return jsonify({"error": "File CSV tidak ditemukan"}), 404

        # 1. LOAD TRAFFIC (Full History)
        df_traffic = pd.read_csv(TRAFFIC_BIG_DATA)
        df_traffic['timestamp'] = pd.to_datetime(df_traffic['timestamp'])
        df_traffic = df_traffic[df_traffic['location_name'] == location_name].copy()

        if df_traffic.empty:
            return jsonify({"error": "Data lokasi kosong"}), 404

        # 2. CHART PREDICTION
        df_traffic['hour'] = df_traffic['timestamp'].dt.hour
        hourly_avg = df_traffic.groupby('hour')['speed_kmh'].mean().round(1)
        
        # Interpolasi & Konversi ke List Python (Agar JSON Aman)
        full_hours = pd.Series(index=range(24), data=np.nan)
        hourly_avg = full_hours.combine_first(hourly_avg).fillna(method='ffill').fillna(method='bfill')
        
        hours_list = [int(x) for x in hourly_avg.index.tolist()]
        speeds_list = [float(x) for x in hourly_avg.values.tolist()]

        # 3. VOLATILITY SCORE
        volatility = float(df_traffic['speed_kmh'].std())
        if pd.isna(volatility): volatility = 0.0
        status_jalan = "Stabil" if volatility < 5 else "Labil"

        # 4. RAIN IMPACT (Data Fusion)
        rain_impact = "Belum Cukup Data"
        
        if os.path.exists(WEATHER_BIG_DATA):
            df_weather = pd.read_csv(WEATHER_BIG_DATA)
            df_weather['waktu'] = pd.to_datetime(df_weather['waktu'])
            df_weather = df_weather[df_weather['nama_lokasi'] == location_name].copy()

            if not df_weather.empty:
                # Merge Data berdasarkan Jam
                df_traffic['join_time'] = df_traffic['timestamp'].dt.round('h')
                df_weather['join_time'] = df_weather['waktu']
                
                df_merge = pd.merge(df_traffic, df_weather, left_on='join_time', right_on='join_time', how='inner')
                
                if not df_merge.empty:
                    # Kode Cuaca >= 50 adalah Hujan
                    df_merge['is_rain'] = df_merge['kode_cuaca'] >= 50
                    avg_speeds = df_merge.groupby('is_rain')['speed_kmh'].mean()

                    # Cek apakah ada data saat Hujan (True) dan Kering (False)
                    if True in avg_speeds.index and False in avg_speeds.index:
                        speed_dry = float(avg_speeds[False])
                        speed_wet = float(avg_speeds[True])
                        
                        drop = 0.0
                        if speed_dry > 0:
                            drop = ((speed_dry - speed_wet) / speed_dry) * 100
                        
                        if drop > 15:
                            rain_impact = f"⚠️ SENSITIF HUJAN (Drop {drop:.1f}%)"
                        elif drop > 5:
                            rain_impact = f"ℹ️ Dampak Sedang (Drop {drop:.1f}%)"
                        else:
                            rain_impact = "✅ Tahan Cuaca"

        return jsonify({
            "hours": hours_list,
            "speeds": speeds_list,
            "volatility": round(volatility, 1),
            "status": status_jalan,
            "rain_impact": rain_impact
        })

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)