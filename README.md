# Label Studio Auto-Annotation Bot

Bot otomasi untuk melakukan anotasi data secara otomatis ke Label Studio berdasarkan hasil (label) yang sudah ada di file Excel (`.xlsx`). Bot ini juga dirancang dengan fitur jeda acak agar perilakunya menyerupai manusia dan tidak terdeteksi sebagai spam.

## Prasyarat

- Python 3.8+
- Akun Label Studio dengan API Key yang aktif
- Project Label Studio yang sudah dibuat (Anda perlu mengetahui Project ID-nya)

## Instalasi

1. **Unduh / Clone Repository**
   Buka Terminal / Command Prompt dan jalankan perintah berikut untuk mengunduh kode dari GitHub:
   ```bash
   git clone https://github.com/Hilal06/LabelStudioBot.git
   cd LabelStudioBot
   ```

2. **Buat Virtual Environment (Sangat Direkomendasikan)**
   Hal ini untuk menghindari konflik dependensi dengan library Python lain di sistem Anda.
   ```bash
   # Membuat virtual environment dengan nama 'venv'
   python3 -m venv venv
   ```

3. **Aktifkan Virtual Environment**
   - Di **Linux / macOS**:
     ```bash
     source venv/bin/activate
     ```
   - Di **Windows**:
     ```bash
     venv\Scripts\activate
     ```

4. **Install Dependensi Library**
   Bot ini membutuhkan library `pandas` (untuk manipulasi data), `openpyxl` (untuk membaca Excel), `label-studio-sdk` (untuk terhubung ke Label Studio), dan `python-dotenv`. Jalankan perintah berikut:
   ```bash
   pip install pandas openpyxl label-studio-sdk python-dotenv
   ```

## Persiapan & Konfigurasi

Sebelum menjalankan bot, Anda perlu memastikan beberapa file dan konfigurasi sudah disiapkan dengan benar.

### 1. Siapkan File Excel (`Annotated_Tweets_Cleaned.xlsx`)
Pastikan file Excel Anda berada di direktori yang sama dengan skrip bot. File Excel ini minimal harus memiliki:
- Kolom `id` (ID yang merujuk ke data asli Anda)
- Kolom label (secara default variabel `LABEL_COLUMN` pada skrip diset ke `sentiment`)

### 2. Atur File Target ID (`test_data.json`)
File ini berfungsi untuk membatasi ID mana saja yang akan dieksekusi (difilter) dari file Excel agar masuk ke Label Studio. Ada 2 format yang didukung:

- **Format Range (Dari X sampai Y):**
  ```json
  {
      "dari": 811,
      "sampai": 815
  }
  ```
- **Format Array (ID Spesifik / Acak):**
  ```json
  [806, 807, 810, 815]
  ```

### 3. Konfigurasi API Key & Parameter
Buat file bernama `.env` di dalam direktori project Anda, lalu masukkan API Key Anda ke dalam file tersebut:
```env
LABEL_STUDIO_API_KEY=API_KEY_ANDA_DI_SINI
```

Buka file `bot_entry_anotation.py` dan sesuaikan ID Project atau URL jika perlu:
```python
LABEL_STUDIO_URL = 'https://bdsrc.binus.ac.id/label-studio/'
PROJECT_ID = 20
```

## Cara Menjalankan Bot

1. Pastikan **Virtual Environment** Anda masih dalam kondisi aktif (lihat Langkah 3 pada Instalasi). Terdapat tulisan `(venv)` di terminal Anda.
   
2. Jalankan skrip Python:
   ```bash
   python3 bot_entry_anotation.py
   ```

3. Anda akan melihat output di terminal tentang proses:
   - Menghubungkan ke API Label Studio.
   - Mengambil daftar task internal.
   - Memfilter data.
   - Memasukkan anotasi (jika berhasil, akan ada jeda `delay` acak 15–30 detik per data layaknya manusia sungguhan).

Jika berhasil dan selesai diproses, sistem akan menampilkan laporan jumlah data yang berhasil dan gagal di-anotasi.
