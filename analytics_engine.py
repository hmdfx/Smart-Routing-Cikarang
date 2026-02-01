import pandas as pd

# Load data 4000 baris kamu
CSV_FILE = "traffic_data_history.csv"

def get_smart_insights():
    try:
        df = pd.read_csv(CSV_FILE)
        
        # 1. Analisis Jam Terburuk (Rush Hour)
        # Kelompokkan data berdasarkan Lokasi & Jam, cari rata-rata speed terendah
        df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        rush_hours = df.groupby(['location_name', 'hour'])['speed_kmh'].mean().reset_index()
        
        # Cari jam dengan speed paling rendah per lokasi
        worst_times = rush_hours.loc[rush_hours.groupby('location_name')['speed_kmh'].idxmin()]
        
        print("\n=== 🕒 PREDIKSI WAKTU TERBURUK (Berdasarkan 4000+ Data) ===")
        for index, row in worst_times.iterrows():
            print(f"📍 {row['location_name']}: Hindari jam {int(row['hour']):02d}:00 (Speed avg: {row['speed_kmh']:.1f} km/h)")

        # 2. Analisis Kestabilan Jalan (Volatility)
        # Semakin tinggi Standar Deviasi, semakin tidak bisa ditebak jalan itu
        volatility = df.groupby('location_name')['speed_kmh'].std().sort_values(ascending=False)
        
        print("\n=== 📈 SKOR KESTABILAN JALAN ===")
        print(f"⚠️ Paling Labil: {volatility.index[0]} (Skor: {volatility.iloc[0]:.1f}) -> Sering macet dadakan!")
        print(f"✅ Paling Stabil: {volatility.index[-1]} (Skor: {volatility.iloc[-1]:.1f}) -> Waktu tempuh terjamin.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_smart_insights()