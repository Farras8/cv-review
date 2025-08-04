# Gunakan base image Python resmi.
FROM python:3.9-slim

# Tetapkan direktori kerja di dalam container.
WORKDIR /app

# Salin file requirements.txt terlebih dahulu untuk memanfaatkan caching layer Docker.
COPY requirements.txt requirements.txt

# Instal dependensi.
RUN pip install --no-cache-dir -r requirements.txt

# Salin file-file contoh CV ke dalam container.
COPY contoh_cv_1.pdf .

# Salin sisa kode aplikasi ke dalam direktori kerja.
COPY main.py .

# Tetapkan perintah default untuk menjalankan aplikasi menggunakan Gunicorn.
# Cloud Run akan secara otomatis menyediakan variabel lingkungan PORT.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
