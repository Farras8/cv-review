# -*- coding: utf-8 -*-
"""
Aplikasi Web Flask untuk Menganalisis CV menggunakan Google Gemini API.

Endpoint /review menerima satu unggahan file PDF dengan form field 'user_cv'.
Aplikasi ini secara otomatis menggunakan dua file PDF contoh yang sudah ada di server
sebagai patokan penilaian.

Aplikasi ini menggunakan kunci API dari Secret Manager Google Cloud.
"""
import os
import json
import sys
import fitz  # PyMuPDF
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
from itertools import cycle

# --- Konfigurasi Aplikasi Flask ---
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# --- Konfigurasi Multi API Key dengan Round-Robin ---
# Di Cloud Run, kunci API akan diambil dari Secret Manager.
# Untuk pengujian lokal, Anda masih bisa menggunakan .env.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("[WARN] Pustaka python-dotenv tidak ditemukan. Mengandalkan variabel lingkungan sistem.")

# Mengambil kunci API dari variabel lingkungan.
api_keys_str = os.environ.get('GOOGLE_API_KEYS')
if not api_keys_str:
    print("KESALAHAN: Variabel lingkungan 'GOOGLE_API_KEYS' tidak diatur.")
    api_keys = []
else:
    api_keys = [key.strip() for key in api_keys_str.split(',') if key.strip()]

if not api_keys:
    print("[WARN] Tidak ada kunci API yang berhasil dimuat. Panggilan API akan gagal.")
    key_cycler = cycle([None]) # Mencegah error jika daftar kosong
else:
    key_cycler = cycle(api_keys)
    print(f"[INFO] Berhasil memuat {len(api_keys)} kunci API untuk digunakan secara round-robin.")

def get_cv_schema():
    """
    Mendefinisikan dan mengembalikan skema JSON untuk output ulasan CV.
    """
    return {
        "type": "OBJECT",
        "properties": {
            "overall_score": {"type": "NUMBER", "description": "Skor keseluruhan dari 0-100 berdasarkan gabungan semua faktor."},
            "scores": {
                "type": "OBJECT",
                "properties": {
                    "ats": {"type": "NUMBER", "description": "Skor keramahan ATS (Applicant Tracking System) dari 0-100."},
                    "format": {"type": "NUMBER", "description": "Skor format dan keterbacaan dari 0-100."},
                    "content": {"type": "NUMBER", "description": "Skor kualitas dan kelengkapan konten dari 0-100."},
                    "impact": {"type": "NUMBER", "description": "Skor dampak dan kuantifikasi pencapaian dari 0-100."}
                }
            },
            "issues": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "title": {"type": "STRING", "description": "Judul singkat dari masalah yang ditemukan."},
                        "description": {"type": "STRING", "description": "Deskripsi detail dari masalah tersebut."},
                        "impact": {"type": "STRING", "description": "Tingkat dampak masalah (Tinggi, Sedang, Rendah)."}
                    }
                }
            },
            "strengths": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "title": {"type": "STRING", "description": "Judul singkat dari kekuatan yang ditemukan."},
                        "description": {"type": "STRING", "description": "Deskripsi detail dari kekuatan tersebut."}
                    }
                }
            },
            "keywords": {
                "type": "OBJECT",
                "properties": {
                    "well_used": {"type": "ARRAY", "items": {"type": "STRING"}, "description": "Kata kunci yang sudah digunakan dengan baik."},
                    "missing": {"type": "ARRAY", "items": {"type": "STRING"}, "description": "Kata kunci relevan yang hilang."},
                    "suggestions": {"type": "ARRAY", "items": {"type": "STRING"}, "description": "Saran kata kunci tambahan."}
                }
            },
            "line_by_line": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "section": {"type": "STRING", "description": "Bagian dari CV yang dianalisis (e.g., Ringkasan, Pengalaman Kerja)."},
                        "whats_working": {"type": "STRING", "description": "Apa yang sudah baik dari bagian ini."},
                        "needs_improvement": {"type": "STRING", "description": "Apa yang perlu ditingkatkan dari bagian ini."}
                    }
                }
            },
            "action_plan": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "week": {"type": "NUMBER", "description": "Nomor minggu untuk rencana aksi."},
                        "focus": {"type": "STRING", "description": "Fokus utama untuk minggu tersebut."},
                        "steps": {"type": "ARRAY", "items": {"type": "STRING"}, "description": "Langkah-langkah konkret yang harus dilakukan."}
                    }
                }
            }
        }
    }

def review_cv_from_text(cv_text: str, all_examples_text: str) -> dict:
    """
    Menganalisis teks CV yang diberikan menggunakan Gemini API dengan beberapa contoh CV sebagai patokan.
    """
    current_key = next(key_cycler)
    if not current_key:
        raise ValueError("Tidak ada kunci API yang tersedia untuk digunakan.")

    print(f"[INFO] Menggunakan API Key yang berakhir dengan '...{current_key[-4:]}'")
    genai.configure(api_key=current_key)

    generation_config = genai.GenerationConfig(
        response_mime_type="application/json",
        response_schema=get_cv_schema()
    )
    model = genai.GenerativeModel(
        "gemini-1.5-flash",
        generation_config=generation_config
    )

    prompt = f"""
      Anda adalah seorang perekrut profesional dan ahli peninjau CV.
      Tugas Anda adalah memberikan ulasan yang komprehensif pada CV pengguna dengan membandingkannya dengan KUMPULAN CONTOH CV yang sangat baik dan ramah ATS.

      --- KUMPULAN CONTOH CV IDEAL (SEBAGAI PATOKAN) ---
      {all_examples_text}
      ---

      Tugas Anda:
      1. Analisis "CV PENGGUNA" di bawah ini secara kritis.
      2. Bandingkan dengan "KUMPULAN CONTOH CV IDEAL" dalam hal kuantifikasi, penggunaan kata kunci, format, dan dampak.
      3. Berikan ulasan lengkap dalam format JSON sesuai skema yang diminta. Fokus pada kesenjangan antara CV pengguna dan contoh-contoh ideal.
      4. Bahasa yang digunakan dalam output harus Bahasa Indonesia.

      --- CV PENGGUNA (UNTUK DIULAS) ---
      {cv_text}
      ---
    """
    
    print("Mengirim permintaan ke Gemini API...")
    response = model.generate_content(prompt)
    return json.loads(response.text)

def extract_text_from_pdf(pdf_source) -> str:
    """
    Membuka file PDF dari stream (unggahan) atau path (lokal) dan mengekstrak teks.
    """
    if isinstance(pdf_source, str): # Jika input adalah path file
        doc = fitz.open(pdf_source)
    else: # Jika input adalah stream file
        doc = fitz.open(stream=pdf_source.read(), filetype="pdf")
    
    text = "".join(page.get_text() for page in doc)
    return text

@app.route("/review", methods=["POST"])
def review_endpoint():
    """Endpoint untuk menerima file PDF dan mengembalikan ulasan CV."""
    if 'user_cv' not in request.files:
        return jsonify({"error": "Permintaan harus menyertakan file dengan form field 'user_cv'."}), 400

    user_cv_file = request.files['user_cv']
    
    # Daftar file contoh PDF yang ada di server
    example_cv_paths = ['contoh_cv_1.pdf']

    try:
        # Ekstrak teks dari CV yang diunggah pengguna
        user_cv_text = extract_text_from_pdf(user_cv_file)
        if not user_cv_text.strip():
            return jsonify({"error": "Gagal mengekstrak teks dari file CV yang diunggah."}), 400
        
        # Ekstrak teks dari file-file contoh
        all_examples_content = []
        for path in example_cv_paths:
            content = extract_text_from_pdf(path)
            if not content:
                raise FileNotFoundError(f"File contoh '{path}' tidak ditemukan atau kosong di server.")
            all_examples_content.append(content)
        
        combined_examples_text = "\n\n--- AKHIR DARI SATU CONTOH, AWAL DARI CONTOH BERIKUTNYA ---\n\n".join(all_examples_content)

        # Kirim untuk diulas
        review_result = review_cv_from_text(user_cv_text, combined_examples_text)
        print("Ulasan CV berhasil dibuat.")
        return jsonify(review_result)

    except Exception as e:
        print(f"[ERROR] Terjadi kesalahan saat memproses permintaan: {e}", file=sys.stderr)
        return jsonify({"error": f"Terjadi kesalahan internal: {str(e)}"}), 500

@app.route("/")
def index():
    """Endpoint root untuk verifikasi bahwa layanan berjalan."""
    return "CV Review Service is running."

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
