## Panduan Menjalankan Dashboard Streamlit

Dashboard ini dibuat menggunakan Streamlit untuk menampilkan visualisasi time series dari data peminjaman sepeda.

### 1. Persyaratan
Sebelum menjalankan dashboard, pastikan Anda telah menginstal Python dan pip.

### 2. Instalasi Dependensi
Jalankan perintah berikut untuk menginstal semua dependensi yang diperlukan:

```sh
pip install -r requirements.txt
```

### 3. Menjalankan Dashboard
Setelah semua dependensi terinstal, jalankan perintah berikut untuk memulai dashboard:

```sh
streamlit run dashboard/dashboard.py
```

Pastikan bahwa file dataset (`day_data.csv` dan `hour_data.csv`) berada di dalam folder `Dashboard/` agar aplikasi dapat berjalan dengan baik
