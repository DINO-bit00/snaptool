<div align="center">

# SnapTool

**Koleksi utilitas dokumen, PDF, dan gambar modern yang berjalan 100% lokal di komputer Anda.**  
Privasi mutlak — tidak ada server pihak ketiga, tidak ada cloud upload, tidak ada pelacakan data.

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-Dark_OLED-38B2AC?logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![PyMuPDF](https://img.shields.io/badge/PyMuPDF-fitz-orange)](https://pymupdf.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen)]()

</div>

---

## 🚀 Cara Install & Menjalankan (Untuk Pemula)

> **Tidak memerlukan keahlian coding.** Cukup ikuti 3 langkah mudah berikut:

### Langkah 1 — Download Python
Pastikan Python sudah terpasang di komputer Anda. Jika belum, unduh di: **[python.org/downloads](https://www.python.org/downloads/)**

> ⚠️ **Penting:** Saat proses instalasi Python, pastikan untuk mencentang opsi **"Add Python to PATH"** di halaman awal installer.

### Langkah 2 — Download SnapTool
Klik tombol hijau **Code → Download ZIP** di repositori ini, lalu ekstrak file ZIP ke folder mana saja di komputer Anda.

### Langkah 3 — Install & Jalankan
Buka folder hasil ekstrak:

1. **Klik dua kali `install.bat`** → tunggu hingga semua dependensi dan library selesai dipasang (membutuhkan koneksi internet untuk unduhan pertama).
2. Setelah selesai, **klik dua kali `start.bat`** untuk meluncurkan SnapTool.
3. Browser akan otomatis terbuka ke alamat `http://localhost:8000` 🎉

> 💡 **Tip:** Untuk pemakaian berikutnya, Anda cukup menjalankan `start.bat` saja tanpa perlu mengulang instalasi.

---

## ✨ Fitur Lengkap

### 📄 1. Konversi Dokumen
| Fitur | Deskripsi | Halaman |
|---|---|---|
| **Word → PDF** | Konversi file `.doc` dan `.docx` ke PDF secara instan dengan dukungan batch upload. | `word-to-pdf.html` |
| **PDF → Word** | Ekstrak teks dan tata letak PDF menjadi dokumen Word (`.docx`) yang dapat diedit. | `pdf-to-word.html` |
| **PDF → Markdown** | Ekstrak teks dan struktur dokumen PDF menjadi format Markdown (`.md`) bersih. | `pdf-to-md.html` |
| **Image → PDF** | Gabungkan hingga 30 gambar (JPG, PNG, WebP) ke dalam satu file PDF A4 dengan tata letak margin kustom dan drag-and-drop reorder. | `img-to-pdf.html` |
| **PDF → Image** | Ekspor halaman dokumen PDF menjadi kumpulan gambar berkualitas tinggi (PNG/JPG). | `pdf-to-img.html` |

### 🔧 2. PDF & Document Tools
| Fitur | Deskripsi | Halaman |
|---|---|---|
| **Merge PDF & Word** | Gabungkan banyak file PDF atau Word menjadi satu kesatuan dokumen dengan pengaturan urutan halaman. | `doc-tools.html` |
| **Split PDF & Word** | Pisahkan dokumen PDF/Word berdasarkan rentang halaman kustom (contoh: `1-5, 6-10, 11-15`) dilengkapi pratinjau live. | `doc-tools.html` |
| **Compress PDF** | Kurangi ukuran file PDF dengan 2 level kompresi (*Standard* untuk menjaga ketajaman teks, *Strong* untuk pemangkasan agresif). | `compress-pdf.html` |
| **Lock / Protect PDF** | Amankan file PDF menggunakan enkripsi password standar industri. | `protect-pdf.html` |
| **Unlock PDF** | Buka dan hapus proteksi password dari file PDF terenkripsi. | `protect-pdf.html` |
| **Watermark Tool** | Tambahkan teks watermark pada dokumen PDF & Gambar dengan **Interactive Live Canvas Preview** (`PDF.js`), pengaturan posisi grid (*Top-Left, Center, Diagonal 45°, Bottom-Right*), ukuran font, opasitas, dan warna kustom. | `watermark.html` |

### 🖼️ 3. Image & AI Tools
| Fitur | Deskripsi | Halaman |
|---|---|---|
| **Background Remover** | Hapus latar belakang foto otomatis menggunakan AI (*rembg*) secara offline dengan dukungan batch processing. | `bg-remover.html` |
| **Smart Crop** | Deteksi dan pemotongan wajah presisi berbasis AI (*OpenCV DNN Face Detection*) untuk pasfoto dan foto profil. | `smart-crop.html` |
| **AI Image Upscaler** | Tingkatkan resolusi gambar hingga **4x** lebih tajam tanpa pecah menggunakan neural network (*Real-ESRGAN NCNN Vulkan* dengan akselerasi GPU). | `image-upscaler.html` |

---

## 🏆 Keunggulan Utama

- **🔒 Privasi 100% Terjaga**: Semua pemrosesan file dieksekusi langsung di mesin lokal komputer Anda. File tidak pernah diunggah ke internet atau server pihak ketiga.
- **🌐 Berjalan Penuh Secara Offline**: Setelah instalasi pertama selesai, seluruh utilitas dapat digunakan tanpa jaringan internet.
- **⚡ Pemrosesan Cepat**: Tanpa latency upload/download jaringan.
- **🎨 Desain Modern & Konsisten**: Tampilan antarmuka *Dark OLED Theme* yang elegan, tipografi premium (*Libre Caslon Text* & *Hanken Grotesk*), dan sepenuhnya responsif di desktop maupun perangkat mobile.
- **📦 Batch Queue Processing**: Dukungan multi-file queue dengan feedback status pemrosesan *real-time*.
- **🆓 Bebas Batasan**: Tanpa batasan ukuran file buatan, tanpa iklan, dan bebas biaya selamanya.

---

## 🛠️ Teknologi & Library

| Komponen | Teknologi |
|---|---|
| **Backend Framework** | [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn ASGI](https://www.uvicorn.org/) |
| **PDF Processing** | [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/) + [pypdf](https://pypdf.readthedocs.io/) + [pdfplumber](https://github.com/jsvine/pdfplumber) |
| **Word Processing** | [docx2pdf](https://github.com/AlJohri/docx2pdf) + [pdf2docx](https://github.com/dothinking/pdf2docx) + [docxcompose](https://github.com/4teamwork/docxcompose) |
| **Image & AI Processing** | [Pillow (PIL)](https://pillow.readthedocs.io/) + [OpenCV](https://opencv.org/) + [rembg](https://github.com/danielgatis/rembg) + [Real-ESRGAN Vulkan](https://github.com/xinntao/Real-ESRGAN) |
| **Frontend UI/UX** | HTML5, Tailwind CSS, Google Fonts, Material Symbols, [PDF.js](https://mozilla.github.io/pdf.js/) |

---

## 📁 Struktur Proyek

```
snaptool/
├── main.py                   # Server API FastAPI & Route Handlers
├── requirements.txt          # Dependensi library Python
├── install.bat               # Script instalasi otomatis (Windows)
├── start.bat                 # Script peluncur server & browser (Windows)
├── static/                   # Antarmuka web frontend (OLED Dark UI)
│   ├── index.html            # Beranda & direktori utilitas
│   ├── word-to-pdf.html      # Konverter Word ke PDF
│   ├── pdf-to-word.html      # Konverter PDF ke Word
│   ├── pdf-to-md.html        # Konverter PDF ke Markdown
│   ├── img-to-pdf.html       # Pembuat PDF dari kumpulan gambar
│   ├── pdf-to-img.html       # Ekstraktor gambar dari halaman PDF
│   ├── doc-tools.html        # Merge & Split Toolkit (PDF & Word)
│   ├── compress-pdf.html     # Pengompres ukuran file PDF
│   ├── protect-pdf.html      # Enkripsi & Pembuka Proteksi PDF
│   ├── watermark.html        # Watermark interaktif (PDF & Gambar)
│   ├── bg-remover.html       # Penghapus latar belakang foto AI
│   ├── smart-crop.html       # Pemotong foto wajah cerdas AI
│   └── image-upscaler.html   # Peningkat resolusi gambar AI (4x)
├── temp/                     # Folder penampung pemrosesan sementara
└── tools/                    # Eksekutabel pihak ketiga (Real-ESRGAN NCNN)
```

---

## 🖥️ Menjalankan Manual (Developer / Advanced User)

Jika Anda ingin menjalankan atau mengembangkan SnapTool secara manual melalui terminal:

```bash
# 1. Clone repositori
git clone https://github.com/DINO-bit00/snaptool.git
cd snaptool

# 2. Buat virtual environment (opsional tetapi disarankan)
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # macOS / Linux

# 3. Pasang dependensi
pip install -r requirements.txt

# 4. Jalankan server Uvicorn
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Buka peramban (*browser*) dan arahkan ke: `http://localhost:8000`

---

## ❓ Pertanyaan yang Sering Diajukan (FAQ)

**Q: Apakah data atau file saya aman saat menggunakan SnapTool?**  
A: Sangat aman. SnapTool berjalan sepenuhnya di komputer Anda sendiri (*localhost*). Tidak ada koneksi transmisi file ke server pihak luar.

**Q: Apakah aplikasi dapat digunakan tanpa koneksi internet?**  
A: Ya. Seluruh fitur bekerja 100% offline setelah proses instalasi dependensi awal selesai.

**Q: Bisakah SnapTool diakses dari perangkat lain (HP / Tablet)?**  
A: Bisa. Jalankan server di komputer Anda, pastikan perangkat lain berada dalam jaringan WiFi yang sama, lalu akses `http://[IP-Komputer-Anda]:8000` melalui browser di HP atau tablet Anda.

---

## 👤 Author

Dibuat oleh **Arya Yusuf Fadilah** © 2026  
*Ilmu Komputer / Informatika — Universitas Bhayangkara Jakarta Raya*  
GitHub: [@DINO-bit00](https://github.com/DINO-bit00)
