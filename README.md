# 🤖 Label Studio Auto-Annotation Bot

Bot ini dibuat untuk membantu Anda melakukan anotasi data secara otomatis ke **Label Studio**. Bot akan membaca hasil label (misalnya sentimen) yang sudah Anda siapkan di file Excel (`.xlsx`) dan memasukkannya ke Label Studio secara otomatis. 

**Fitur Unggulan:** 
Bot ini memiliki fitur "jeda acak" (random delay) antara 15-30 detik pada setiap pengisian data. Hal ini membuat bot terlihat seperti manusia yang sedang bekerja (human-like) dan mencegah akun Anda terdeteksi sebagai bot atau spam oleh server.

---

## 📋 Persiapan (Prasyarat)
Sebelum memulai, pastikan Anda sudah memiliki:
1. **Python** versi 3.8 atau yang lebih baru terinstal di komputer/laptop Anda.
2. Akun **Label Studio** yang sudah memiliki **API Key** aktif.
3. Sebuah **Project di Label Studio** yang sudah siap menampung anotasi data (Anda perlu mengetahui ID Project-nya).

---

## 🛠️ Langkah-langkah Instalasi

Ikuti langkah-langkah di bawah ini secara berurutan:

### 1. Unduh Kode Bot (Clone Repository)
Buka aplikasi **Terminal** (di macOS/Linux) atau **Command Prompt / PowerShell** (di Windows), lalu jalankan perintah ini:
```bash
git clone https://github.com/Hilal06/LabelStudioBot.git
cd LabelStudioBot
```

### 2. Buat "Ruang Kerja" Khusus (Virtual Environment)
*Catatan pemula: Virtual environment sangat penting agar aplikasi bot ini tidak merusak atau berbenturan dengan aplikasi Python lain di komputer Anda.*

Jalankan perintah ini untuk membuat ruang kerja khusus bernama `venv`:
```bash
python3 -m venv venv
```

### 3. Aktifkan Ruang Kerja Tersebut
Anda harus mengaktifkannya setiap kali ingin menjalankan bot.
- **Untuk pengguna Windows:**
  ```bash
  venv\Scripts\activate
  ```
- **Untuk pengguna Linux / macOS:**
  ```bash
  source venv/bin/activate
  ```
*(Jika berhasil diaktifkan, biasanya akan muncul tulisan `(venv)` di depan baris terminal Anda).*

### 4. Install Bahan-bahan yang Dibutuhkan
Bot ini membutuhkan beberapa alat bantuan (library). Install semuanya sekaligus dengan perintah ini:
```bash
pip install pandas openpyxl label-studio-sdk python-dotenv
```

---

## ⚙️ Pengaturan Sebelum Dijalankan (Konfigurasi)

### 1. Siapkan Kunci API (API Key)
Bot butuh kunci agar bisa masuk ke akun Label Studio Anda.
1. Buat sebuah file baru bernama `.env` (pastikan ada titik di depannya) di dalam folder `LabelStudioBot`.
2. Isi file tersebut dengan teks seperti di bawah ini, lalu ganti dengan API Key Anda yang asli:
   ```env
   LABEL_STUDIO_API_KEY=KODE_API_KEY_ANDA_DI_SINI
   ```

### 2. Siapkan File Excel Anda
Pastikan file Excel yang berisi data Anda (misal: `Annotated_Tweets_Cleaned.xlsx`) diletakkan di dalam folder yang sama dengan bot ini. File tersebut harus memiliki:
- Kolom bernama `id` (sebagai penanda unik setiap data).
- Kolom berisi hasil label Anda (misal: kolom bernama `sentiment`).

### 3. Sesuaikan File Python Bot
Buka file `bot_entry_anotation.py` menggunakan teks editor (Notepad, VS Code, dll). Cari bagian ini dan sesuaikan dengan milik Anda:
```python
LABEL_STUDIO_URL = 'https://bdsrc.binus.ac.id/label-studio/' # Ganti jika URL Label Studio Anda berbeda
PROJECT_ID = 20 # Ganti dengan ID Project Anda
```

### 4. Pilih Data yang Ingin Diproses (Target ID)
Anda bisa mengatur bot agar hanya memproses data tertentu saja dengan mengubah isi file `test_data.json`.
Ada dua cara pengisian:

- **Cara 1: Jarak / Rentang (Dari angka X sampai Y)**
  ```json
  {
      "dari": 811,
      "sampai": 815
  }
  ```
- **Cara 2: Pilih ID Spesifik / Acak**
  ```json
  [806, 807, 810, 815]
  ```

---

## 🚀 Cara Menjalankan Bot

Jika semua persiapan di atas sudah selesai, saatnya menjalankan bot:

1. Pastikan **Virtual Environment** masih menyala (ada tulisan `(venv)` di terminal).
2. Ketik perintah ini dan tekan Enter:
   ```bash
   python3 bot_entry_anotation.py
   ```
3. **Selesai!** Anda bisa bersantai melihat bot bekerja di terminal Anda. Bot akan:
   - Menghubungkan diri ke Label Studio.
   - Menyaring data yang perlu dikerjakan sesuai `test_data.json`.
   - Mengisi data satu per satu, sambil **beristirahat acak 15-30 detik** setiap kali selesai mengisi satu data agar terlihat natural seperti manusia.

Di akhir proses, bot akan memberikan laporan berapa banyak data yang berhasil dan gagal diisi.
