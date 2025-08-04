import requests
import json

# Ganti dengan URL layanan Cloud Run Anda jika sudah di-deploy
API_URL = "https://cv-review-service-819767094904.asia-southeast2.run.app/review" 

# Ganti dengan path ke file CV yang ingin Anda uji
CV_FILE_PATH = "Muhammad Fadhl Ivander Virajati - CV.pdf" 

print(f"Mengirim file '{CV_FILE_PATH}' ke {API_URL}...")

try:
    with open(CV_FILE_PATH, 'rb') as cv_file:
        # Nama 'user_cv' harus cocok dengan yang ada di main.py
        files = {'user_cv': (CV_FILE_PATH, cv_file, 'application/pdf')}
        
        # Kirim permintaan POST
        response = requests.post(API_URL, files=files)

    # Periksa status respons
    response.raise_for_status()  # Ini akan error jika status bukan 2xx

    print("\nRespons berhasil diterima!")
    print("Status Code:", response.status_code)
    
    # Cetak hasil JSON dengan format yang rapi
    review_data = response.json()
    print("\n--- HASIL REVIEW CV ---")
    print(json.dumps(review_data, indent=2, ensure_ascii=False))

except requests.exceptions.HTTPError as http_err:
    print(f"\nHTTP error terjadi: {http_err}")
    print("Isi Respons:", response.text)
except Exception as err:
    print(f"\nError lain terjadi: {err}")