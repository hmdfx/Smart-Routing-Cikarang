// ================= KONFIGURASI =================
// Ganti dengan API Key TomTom kamu jika belum ada
const TOMTOM_KEY = 'xxxxx'; 

const COORDS = {
    'Terminal Cikarang':      '-6.2619,107.1379',
    'Sentra Grosir Cikarang': '-6.2584,107.1462',
    'Stasiun Cikarang':       '-6.2536,107.1422',
    'Lippo Mall Cikarang':    '-6.3341,107.1369',
    'President University':   '-6.2850,107.1706'
};

// ================= INIT PETA =================
var map = L.map('map').setView([-6.265, 107.15], 13);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { 
    attribution: '© OpenStreetMap' 
}).addTo(map);

var routeLayer = null;
var startMarker = null;
var endMarker = null;
let trafficChart = null; // [BARU] Variabel untuk Grafik Chart.js

// ================= HELPER: TERJEMAHKAN KODE CUACA =================
function getWeatherDesc(code) {
    if (code === 0) return "☀️ Cerah";
    if (code === 1 || code === 2 || code === 3) return "☁️ Berawan";
    if (code === 45 || code === 48) return "🌫️ Berkabut";
    if (code >= 51 && code <= 55) return "🌧️ Gerimis";
    if (code >= 61 && code <= 65) return "🌧️ Hujan";
    if (code >= 80 && code <= 82) return "🌦️ Hujan Lokal";
    if (code >= 95) return "⚡ Badai Petir";
    return "❓ (" + code + ")";
}

// ================= EVENT LISTENER =================
document.getElementById('btnCalculate').addEventListener('click', calculateSmartETA);

// ================= FUNGSI UTAMA =================
async function calculateSmartETA() {
    var startName = document.getElementById('startLoc').value;
    var endName = document.getElementById('endLoc').value;

    if(startName === endName) {
        alert("Lokasi Asal & Tujuan tidak boleh sama!");
        return;
    }

    // --- 1. UPDATE MARKER DI PETA ---
    if (startMarker) map.removeLayer(startMarker);
    if (endMarker) map.removeLayer(endMarker);

    var startLatLong = COORDS[startName].split(',');
    var endLatLong = COORDS[endName].split(',');

    startMarker = L.marker(startLatLong).addTo(map)
        .bindPopup("📍 " + startName).openPopup();

    endMarker = L.marker(endLatLong).addTo(map)
        .bindPopup("🏁" + endName);

    // ============================================================
    // [BARU] STEP 3: PANGGIL FUNGSI ANALYTICS (TAMPILKAN GRAFIK)
    // ============================================================
    // Kita load analitik untuk lokasi ASAL agar user tau kondisi start point
    loadAnalytics(startName);


    // --- 2. AMBIL KONDISI REAL-TIME DARI BACKEND ---
    let conditions = null;
    try {
        let res = await fetch(`/api/get_conditions/${startName}/${endName}`);
        conditions = await res.json();
        
        // Update UI
        document.getElementById('conditionCard').style.display = 'block';
        
        // Asal
        document.getElementById('sSpeed').innerText = conditions.start.speed + " km/h";
        document.getElementById('sTemp').innerText = conditions.start.temp + "°C";
        document.getElementById('sWeather').innerText = getWeatherDesc(conditions.start.weather_code);
        document.getElementById('sRain').innerText = conditions.start.rain + " mm";
        
        // Tujuan
        document.getElementById('eSpeed').innerText = conditions.end.speed + " km/h";
        document.getElementById('eTemp').innerText = conditions.end.temp + "°C";
        document.getElementById('eWeather').innerText = getWeatherDesc(conditions.end.weather_code);
        document.getElementById('eRain').innerText = conditions.end.rain + " mm";
        
    } catch (e) { console.error("Gagal ambil kondisi:", e); }


    // --- 3. LOGIKA WEATHER IMPACT (SMART ETA) ---
    let avgRain = 0;
    if (conditions) {
        avgRain = (conditions.start.rain + conditions.end.rain) / 2;
    }

    let impactFactor = 1.0; 
    let msg = "";
    let alertBox = document.getElementById('weatherAlert');

    if (avgRain > 7.0) {
        impactFactor = 1.35; 
        msg = "⚠️ HUJAN DERAS! Estimasi waktu ditambah signifikan (+35%).";
        alertBox.style.color = "#721c24";
        alertBox.style.backgroundColor = "#f8d7da";
    } else if (avgRain > 0.5) {
        impactFactor = 1.15; 
        msg = "🌧️ Jalan Basah. Waktu sedikit lebih lama (+15%).";
        alertBox.style.color = "#856404";
        alertBox.style.backgroundColor = "#fff3cd";
    } else {
        msg = "✅ Cuaca Kondusif. Tidak ada delay cuaca.";
        alertBox.style.color = "#155724";
        alertBox.style.backgroundColor = "#d4edda";
    }

    alertBox.innerText = msg;
    alertBox.style.display = 'block';


    // --- 4. REQUEST ROUTE TOMTOM ---
    var url = `https://api.tomtom.com/routing/1/calculateRoute/${COORDS[startName]}:${COORDS[endName]}/json?key=${TOMTOM_KEY}&traffic=true`;
    
    try {
        let res = await fetch(url);
        let json = await res.json();
        
        if(json.routes && json.routes.length > 0) {
            let route = json.routes[0];
            let baseSeconds = route.summary.travelTimeInSeconds;
            let smartSeconds = baseSeconds * impactFactor;

            let baseMin = Math.round(baseSeconds / 60);
            let smartMin = Math.round(smartSeconds / 60);

            document.getElementById('resultCard').style.display = 'block';
            document.getElementById('distVal').innerText = (route.summary.lengthInMeters / 1000).toFixed(1) + " km";
            document.getElementById('baseEta').innerText = baseMin + " menit";
            document.getElementById('finalEta').innerText = smartMin + " menit";
            
            if(routeLayer) map.removeLayer(routeLayer);
            let points = route.legs[0].points.map(p => [p.latitude, p.longitude]);
            let lineColor = impactFactor > 1.0 ? '#dc3545' : '#007bff'; 
            
            routeLayer = L.polyline(points, {color: lineColor, weight: 6, opacity: 0.8}).addTo(map);
            
            var group = new L.featureGroup([startMarker, endMarker, routeLayer]);
            map.fitBounds(group.getBounds(), {padding: [50, 50]});
        }
    } catch (e) { 
        alert("Gagal koneksi ke TomTom: " + e); 
        console.error(e);
    }
}

// ============================================================
// [BARU] FUNGSI STEP 3: LOGIKA CHART.JS & ANALYTICS
// ============================================================

async function loadAnalytics(locationName) {
    try {
        let res = await fetch(`/api/analytics/${locationName}`);
        let data = await res.json();

        if (data.error) return;

        document.getElementById('analyticsCard').style.display = 'block';
        
        // Tampilkan 2 Baris Status: Volatilitas & Dampak Hujan
        let statusHTML = `
            <div style="margin-bottom:5px;">🚦 <b>${data.status}</b> (Volatilitas: ${data.volatility})</div>
            <div style="font-size:13px; color:#d63384;">🌧️ <b>${data.rain_impact}</b></div>
        `;
        
        document.getElementById('algoStatus').innerHTML = statusHTML;

        renderChart(data.hours, data.speeds);

    } catch (e) {
        console.error("Gagal load analytics:", e);
    }
}

function renderChart(labels, dataPoints) {
    const ctx = document.getElementById('predictionChart').getContext('2d');

    // Hapus chart lama jika ada (agar tidak menumpuk)
    if (trafficChart) {
        trafficChart.destroy();
    }

    // Buat Chart Baru
    trafficChart = new Chart(ctx, {
        type: 'line', // Grafik Garis
        data: {
            labels: labels.map(h => `${h}:00`), // Label Sumbu X (Jam)
            datasets: [{
                label: 'Kecepatan Rata-rata (km/h)',
                data: dataPoints,
                borderColor: '#007bff', // Warna Garis Biru
                backgroundColor: 'rgba(0, 123, 255, 0.1)', // Warna Arsiran Bawah
                borderWidth: 2,
                tension: 0.4, // Membuat garis melengkung halus (Spline)
                pointRadius: 2,
                fill: true
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: 'Kecepatan (km/h)' }
                }
            },
            plugins: {
                legend: { display: false } // Sembunyikan legenda agar rapi
            }
        }
    });
}