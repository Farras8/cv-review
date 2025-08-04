# -*- coding: utf-8 -*-
"""
Skrip Python untuk Memverifikasi Koneksi beberapa Google Gemini API Keys.

Membaca variabel lingkungan 'GOOGLE_API_KEYS' dari file .env,
yang berisi satu atau lebih kunci API yang dipisahkan koma.
"""
import os
import sys
import google.generativeai as genai
from dotenv import load_dotenv

# Muat variabel dari file .env
load_dotenv()

def check_multiple_api_keys():
    """
    Memeriksa konektivitas dan validitas untuk daftar kunci API Gemini.
    """
    print("--- Memulai Pengecekan Koneksi Multi-API Key Gemini ---")

    # Membaca variabel lingkungan setelah dimuat oleh dotenv
    api_keys_str = os.environ.get('GOOGLE_API_KEYS')
    if not api_keys_str:
        print("[GAGAL] Variabel lingkungan 'GOOGLE_API_KEYS' tidak diatur atau kosong.")
        print("       Harap atur kunci API Anda di file .env (dipisahkan koma jika lebih dari satu).")
        sys.exit(1)

    api_keys = [key.strip() for key in api_keys_str.split(',') if key.strip()]
    print(f"[INFO] Ditemukan {len(api_keys)} kunci API untuk diuji.")

    success_count = 0
    failure_count = 0

    for i, api_key in enumerate(api_keys):
        key_display_name = f"Kunci #{i + 1} (berakhir dengan '...{api_key[-4:]}')"
        print(f"\n--- Menguji {key_display_name} ---")

        try:
            genai.configure(api_key=api_key)
            print(f"[OK] {key_display_name}: Pustaka berhasil dikonfigurasi.")

            print(f"Mengirim permintaan tes untuk {key_display_name}...")
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content("Sebutkan satu fakta menarik tentang teknologi.")

            if response.text:
                print(f"[OK] {key_display_name}: Berhasil menerima respons dari Gemini API.")
                success_count += 1
            else:
                print(f"[GAGAL] {key_display_name}: Respons diterima, tetapi tidak berisi teks.")
                if hasattr(response, 'prompt_feedback'):
                    print("       Prompt Feedback:", response.prompt_feedback)
                failure_count += 1

        except Exception as e:
            print(f"[GAGAL] {key_display_name}: Terjadi kesalahan saat berkomunikasi dengan Gemini API.")
            print(f"       Detail Kesalahan: {e}")
            failure_count += 1

    print("\n" + "="*20 + " Ringkasan Pengecekan " + "="*20)
    print(f"Total Kunci Diuji: {len(api_keys)}")
    print(f"Berhasil: {success_count}")
    print(f"Gagal: {failure_count}")
    print("="*62 + "\n")

    if failure_count > 0:
        print("Beberapa kunci API gagal divalidasi. Harap periksa detail kesalahan di atas.")
    else:
        print("Semua kunci API berhasil divalidasi!")

if __name__ == "__main__":
    check_multiple_api_keys()
