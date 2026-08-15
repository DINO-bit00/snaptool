<div align="center">

# SnapTool

**Koleksi utilitas dokumen dan gambar yang berjalan 100% di komputer Anda sendiri.**  
Tidak ada server pihak ketiga, tidak ada upload ke internet, tidak ada tracking.

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen)]()

</div>

---

## 🚀 Cara Install (untuk semua orang)

> **Tidak perlu paham coding sama sekali.** Ikuti 3 langkah berikut:

### Langkah 1 — Download Python
Kalau belum punya Python, download dulu di: **[python.org/downloads](https://www.python.org/downloads/)**

> ⚠️ **Penting:** Saat install, centang kotak **"Add Python to PATH"** di halaman pertama installer.

### Langkah 2 — Download SnapTool
Klik tombol **Code → Download ZIP** di halaman ini, lalu ekstrak ke folder mana saja.

### Langkah 3 — Install & Jalankan
Masuk ke folder hasil ekstrak, lalu:

1. **Klik dua kali `install.bat`** → tunggu sampai semua library terinstall (butuh internet, ~5 menit pertama kali)
2. Setelah selesai, **klik dua kali `start.bat`** setiap kali ingin membuka SnapTool
3. Browser akan terbuka otomatis ke `http://localhost:8000` ✅

> 💡 Setelah install pertama kali, untuk pemakaian selanjutnya cukup klik `start.bat` saja — tidak perlu install ulang.

---

## ✨ Fitur Lengkap

### 📄 Konversi Dokumen
| Fitur | Deskripsi |
|-------|-----------|
| **Word → PDF** | Konversi file `.doc` dan `.docx` ke PDF. Mendukung upload banyak file sekaligus |
| **PDF → Word** | Ekstrak teks dan layout dari PDF menjadi dokumen Word (`.docx`) yang bisa diedit |
| **Image → PDF** | Gabungkan beberapa gambar (JPG, PNG, WEBP) menjadi satu file PDF |
| **PDF → Image** | Ekspor setiap halaman PDF menjadi file gambar terpisah (PNG/JPG) |

### 🔧 PDF Tools
| Fitur | Deskripsi |
|-------|-----------|
| **Merge PDF** | Gabungkan beberapa file PDF menjadi satu dokumen, dengan pengaturan urutan |
| **Split PDF** | Pisahkan halaman-halaman PDF berdasarkan rentang yang Anda tentukan (mis: `1-3, 5, 7-9`) |
| **Merge Word** | Gabungkan beberapa file Word menjadi satu dokumen |
| **Split Word** | Pisahkan dokumen Word berdasarkan nomor halaman |
| **Compress PDF** | Kurangi ukuran file PDF. Mode *Standard* menjaga teks tetap bisa diblok; Mode *Strong* memangkas ukuran secara maksimal |
| **Lock PDF** | Lindungi PDF dengan password — tidak bisa dibuka tanpa kata sandi |
| **Unlock PDF** | Hapus password dari PDF terenkripsi |

### 🖼️ Image Tools
| Fitur | Deskripsi |
|-------|-----------|
| **Background Remover** | Hapus latar belakang dari foto/gambar secara otomatis menggunakan AI. Mendukung batch processing |
| **Smart Crop** | Pemotongan wajah cerdas otomatis menggunakan AI (OpenCV DNN Face Detection) untuk membuat foto profil/pasfoto presisi |
| **AI Image Upscaler** | Memperbesar resolusi gambar hingga 4x tanpa pecah menggunakan AI (Real-ESRGAN NCNN Vulkan), dioptimalkan dengan GPU |

---

## 🏆 Keunggulan SnapTool

- **🔒 100% Privasi** — Semua file diproses di komputer Anda sendiri. Tidak ada satu pun file yang dikirim ke internet atau server manapun.
- **🌐 Bisa Offline** — Setelah diinstall, SnapTool bisa digunakan tanpa koneksi internet sama sekali (kecuali Background Remover untuk download model AI pertama kali).
- **⚡ Cepat** — Tidak perlu menunggu upload/download ke server. Kompresi dan konversi berjalan langsung di mesin Anda.
- **🆓 Gratis Selamanya** — Tidak ada biaya langganan, tidak ada batasan jumlah file, tidak ada watermark.
- **🎨 UI Modern** — Desain editorial minimalis yang bersih dengan dukungan **Dark Mode**. Nyaman dipakai siang maupun malam.
- **📦 Batch Processing** — Hampir semua fitur mendukung upload dan pemrosesan banyak file sekaligus.
- **🔄 Antrian Cerdas** — File diproses satu per satu secara otomatis dengan tampilan status real-time.

---

## 🛠️ Teknologi yang Digunakan

| Komponen | Teknologi |
|----------|-----------|
| Backend Server | [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/) |
| Manipulasi PDF | [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/) + [pypdf](https://pypdf.readthedocs.io/) |
| Konversi Word ↔ PDF | [docx2pdf](https://github.com/AlJohri/docx2pdf) + [pdf2docx](https://github.com/dothinking/pdf2docx) |
| Hapus Background AI | [rembg](https://github.com/danielgatis/rembg) |
| Image Processing AI | [OpenCV](https://opencv.org/) + [Real-ESRGAN (NCNN Vulkan)](https://github.com/xinntao/Real-ESRGAN) |
| Merge/Split Word | [docxcompose](https://github.com/4teamwork/docxcompose) |
| Frontend | HTML, Vanilla CSS, Vanilla JS |

---

## 📁 Struktur Folder

```
snaptool/
├── main.py              ← Backend server (FastAPI)
├── requirements.txt     ← Daftar library Python
├── install.bat          ← Script installer (klik untuk install)
├── start.bat            ← Script untuk menjalankan aplikasi
├── static/              ← Halaman-halaman antarmuka (HTML/CSS/JS)
│   ├── index.html
│   ├── word-to-pdf.html
│   ├── pdf-to-word.html
│   ├── img-to-pdf.html
│   ├── pdf-to-img.html
│   ├── doc-tools.html
│   ├── compress-pdf.html
│   ├── protect-pdf.html
│   ├── bg-remover.html
│   ├── smart-crop.html
│   ├── image-upscaler.html
│   ├── theme.css        ← Dark mode styling
│   └── theme.js         ← Dark mode toggle logic
├── temp/                ← Folder sementara untuk file yang diproses
├── tools/               ← Eksekutabel pihak ketiga (contoh: Real-ESRGAN)
└── models/              ← Model AI yang di-download otomatis
```

---

## 🖥️ Cara Jalankan Manual (untuk pengguna tingkat lanjut)

```bash
# Clone repository
git clone https://github.com/DINO-bit00/snaptool.git
cd snaptool

# Install dependencies
pip install -r requirements.txt

# Jalankan server
uvicorn main:app --host 0.0.0.0 --port 8000
```

Buka browser dan akses: `http://localhost:8000`

---

## ❓ FAQ

**Q: Apakah file saya aman?**  
A: Ya, 100%. Semua pemrosesan terjadi di komputer Anda sendiri. File Anda tidak pernah meninggalkan perangkat.

**Q: Bisa dipakai tanpa internet?**  
A: Bisa! Setelah instalasi pertama, SnapTool bisa dijalankan sepenuhnya offline.

**Q: Kenapa Background Remover butuh waktu lebih lama pertama kali?**  
A: Karena model AI-nya (~170 MB) perlu didownload sekali saat pertama dipakai. Setelah itu, prosesnya akan jauh lebih cepat.

**Q: Apakah bisa diakses dari HP?**  
A: Bisa! Jalankan server di laptop/komputer, lalu dari HP di jaringan WiFi yang sama, akses `http://[IP-komputer]:8000`.

---

## 👤 Author

Dibuat oleh **Arya Yusuf Fadilah** © 2026  
Ilmu Komputer/Informatika — Universitas Bhayangkara Jakarta Raya
