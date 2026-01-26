import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ================= KONFIGURASI =================
CSV_FILENAME = "traffic_weather_data.csv"

def visualize_data():
    try:
        # 1. Baca Data
        df = pd.read_csv(CSV_FILENAME)
        
        # Konversi kolom timestamp agar dikenali sebagai waktu
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Set Style Grafik
        sns.set_theme(style="whitegrid")
        plt.figure(figsize=(15, 10))

        # --- GRAFIK 1: Kecepatan Rata-rata per Lokasi ---
        plt.subplot(2, 1, 1) # Baris 1
        sns.lineplot(data=df, x='timestamp', y='speed_kmh', hue='location_name', marker='o')
        plt.title('Monitoring Kecepatan Lalu Lintas (Real-time)', fontsize=14)
        plt.ylabel('Kecepatan (km/h)')
        plt.xlabel('Waktu')
        plt.legend(title='Lokasi')

        # --- GRAFIK 2: Hubungan Hujan vs Kemacetan (Delay) ---
        # Kita ingin melihat: Apakah saat Hujan (Rain > 0), Delay naik?
        plt.subplot(2, 1, 2) # Baris 2
        
        # Membuat dual axis (Sumbu kiri: Delay, Sumbu kanan: Curah Hujan)
        ax1 = plt.gca()
        sns.lineplot(data=df, x='timestamp', y='delay_seconds', hue='location_name', ax=ax1, linestyle='--')
        ax1.set_ylabel('Delay / Keterlambatan (Detik)', color='blue')
        ax1.tick_params(axis='y', labelcolor='blue')
        
        # Sumbu kanan untuk Hujan (Kita ambil rata-rata hujan semua lokasi sebagai background)
        ax2 = ax1.twinx()
        sns.barplot(data=df, x='timestamp', y='rain_mm', color='gray', alpha=0.3, ax=ax2, errorbar=None)
        ax2.set_ylabel('Curah Hujan (mm)', color='gray')
        ax2.set_ylim(0, 10) # Set limit visual hujan agar tidak menutupi grafik
        
        plt.title('Dampak Hujan terhadap Delay (ETA)', fontsize=14)
        plt.tight_layout()
        
        # Tampilkan
        print("Menampilkan grafik...")
        plt.show()

    except FileNotFoundError:
        print("File CSV belum ditemukan! Jalankan data_collector.py dulu.")
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")

if __name__ == "__main__":
    visualize_data()