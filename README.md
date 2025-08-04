# CV Review Service

Aplikasi web berbasis Flask untuk menganalisis dan menilai CV secara otomatis menggunakan Google Gemini API. Model ini dirancang untuk membantu pengguna mendapatkan ulasan komprehensif terhadap CV mereka, membandingkan dengan contoh CV ideal, dan memberikan saran perbaikan yang terstruktur.

## Fitur Utama
- **Analisis CV Otomatis:** Menggunakan Gemini API untuk menilai CV berdasarkan format, konten, kata kunci, dan dampak pencapaian.
- **Multi-API Key Support:** Mendukung penggunaan beberapa kunci API secara round-robin untuk menghindari limitasi kuota.
- **CORS Enabled:** Mendukung akses dari frontend web (misal: React/Vue) melalui konfigurasi CORS.
- **Contoh CV Ideal:** CV pengguna dibandingkan dengan satu atau lebih contoh CV ideal yang sudah ada di server.
- **Output JSON Terstruktur:** Hasil ulasan dikembalikan dalam format JSON sesuai skema yang telah ditentukan.

## Cara Kerja
1. Pengguna mengunggah file CV (PDF) melalui endpoint `/review`.
2. Server mengekstrak teks dari CV pengguna dan contoh CV ideal.
3. Teks dikirim ke Gemini API untuk dianalisis.
4. Hasil ulasan dikembalikan dalam format JSON yang berisi skor, kekuatan, masalah, kata kunci, dan rencana aksi.

## Instalasi Lokal
1. **Clone repository:**
   ```bash
   git clone https://github.com/Farras8/cv-review.git
   cd cv-review
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Konfigurasi API Key:**
   - Buat file `.env` dan isi dengan:
     ```env
     GOOGLE_API_KEYS=key1,key2,key3
     ```
4. **Jalankan aplikasi:**
   ```bash
   python main.py
   ```

## Deployment ke Cloud Run
- Gunakan `Dockerfile` dan `cloudbuild.yaml` untuk membangun dan deploy ke Google Cloud Run.
- Kunci API dapat diatur melalui Secret Manager dan di-inject sebagai environment variable.

## Endpoint
- `POST /review` : Menerima file PDF CV dan mengembalikan ulasan JSON.
- `GET /` : Mengecek status layanan.

## Skema Output JSON
Output ulasan CV mengikuti skema berikut:
- `overall_score`: Skor keseluruhan.
- `scores`: Skor per aspek (ATS, format, konten, impact).
- `issues`: Daftar masalah yang ditemukan.
- `strengths`: Daftar kekuatan CV.
- `keywords`: Kata kunci yang digunakan, hilang, dan saran.
- `line_by_line`: Analisis per bagian CV.
- `action_plan`: Rencana aksi mingguan untuk perbaikan CV.

## Lisensi
MIT

---

**CV Review Service** membantu Anda mendapatkan feedback profesional dan terstruktur untuk meningkatkan kualitas CV Anda secara otomatis.
