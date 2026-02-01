# 🚗 Smart Route Cikarang (Traffic & Weather Intelligence)

**Smart Route Cikarang** adalah aplikasi dashboard berbasis web yang memonitor kondisi lalu lintas dan cuaca secara real-time di wilayah Cikarang. Aplikasi ini menggabungkan data lalu lintas (Traffic) dan data cuaca (Weather) untuk menghasilkan estimasi waktu tiba (**Smart ETA**) yang lebih akurat dibandingkan navigasi biasa.

Sistem ini menerapkan konsep **Data Fusion**, di mana kondisi hujan deras atau jalan basah akan secara otomatis menambahkan "faktor penalti" pada waktu tempuh yang dihitung oleh TomTom API.

![Dashboard Preview](https://pasteboard.co/TRUKDPkuadET.png)

---

## ✨ Fitur Utama

1.  **Monitoring Kecepatan Real-time:** Menampilkan kecepatan rata-rata (km/h) di 5 titik vital Cikarang (Terminal, SGC, Stasiun, Lippo Mall, President University).
2.  **Integrasi Data Cuaca:** Menampilkan suhu (°C), kondisi cuaca (Cerah/Hujan), dan curah hujan (mm) pada titik asal dan tujuan.
3.  **Smart ETA Calculation:** Logika cerdas yang menyesuaikan estimasi waktu tiba berdasarkan intensitas hujan:
    * **Hujan Deras:** Menambahkan estimasi waktu sebesar **35%**.
    * **Hujan Ringan:** Menambahkan estimasi waktu sebesar **15%**.
    * **Cuaca Kondusif:** Menggunakan ETA standar.
4.  **Visualisasi Peta Interaktif:** Menggunakan OpenStreetMap dan Leaflet.js untuk menampilkan rute, marker lokasi, dan perubahan warna jalur (Biru = Aman, Merah = Delay Cuaca).

---

## 🛠️ Teknologi yang Digunakan

* **Backend:** Python (Flask), Pandas.
* **Frontend:** HTML5, CSS3, JavaScript (Leaflet.js).
* **API & Data Source:**
    * **TomTom API:** Untuk data Traffic Flow & Routing.
    * **Open-Meteo:** Untuk data Weather Forecast (CSV Generation).
    * **CSV Database:** Penyimpanan data lokal (`traffic_weather_data.csv`, `weather_data.csv`).

---

## 📂 Struktur Proyek


```text
/Smart_Route_Cikarang
│
├── app.py                   # Server Web (Flask) & API Backend
├── data_collector.py        # Script untuk mengambil data Traffic & Weather ke CSV
├── traffic_weather_data.csv # Database Traffic (Generated)
├── weather_data.csv         # Database Weather (Generated)
│
├── templates/
│   └── index.html           # Halaman Utama (Frontend)
│
└── static/
    ├── style.css            # Styling Tampilan
    └── script.js            # Logika Peta & Smart ETA




    🚀 Cara Instalasi & Menjalankan
1. Prasyarat (Prerequisites)

Pastikan Python sudah terinstall. Install library yang dibutuhkan:
Bash

pip install flask pandas requests

2. Konfigurasi API Key

    Dapatkan API Key gratis dari TomTom Developer Portal.

    Buka file static/script.js dan masukkan API Key:
    JavaScript

    const TOMTOM_KEY = 'MASUKKAN_API_KEY_KAMU_DISINI';

    (Opsional) Jika data_collector.py membutuhkan key, masukkan juga di sana.

3. Generate Data Awal

Sebelum menjalankan web, pastikan file CSV sudah tersedia. Jalankan script pengumpul data:
Bash

python data_collector.py

Biarkan script ini berjalan di background agar data selalu update.
4. Jalankan Server Web

Buka terminal baru dan jalankan:
Bash

python app.py

5. Akses Dashboard

Buka browser dan kunjungi: 👉 http://127.0.0.1:5000


👨‍💻 Author

Ahmad Abdul Hamid Information System Student - President University