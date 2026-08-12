@echo off
chcp 65001 >nul
title SnapTool - Installer

echo.
echo  ██████╗██╗  ██╗ █████╗ ██████╗ ████████╗ ██████╗  ██████╗ ██╗
echo ██╔════╝██║  ██║██╔══██╗██╔══██╗╚══██╔══╝██╔═══██╗██╔═══██╗██║
echo ╚█████╗ ███████║███████║██████╔╝   ██║   ██║   ██║██║   ██║██║
echo  ╚═══██╗██╔══██║██╔══██║██╔═══╝    ██║   ██║   ██║██║   ██║██║
echo ██████╔╝██║  ██║██║  ██║██║        ██║   ╚██████╔╝╚██████╔╝███████╗
echo ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝        ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝
echo.
echo  Installer otomatis - cukup tunggu sampai selesai!
echo ============================================================
echo.

:: ─── LANGKAH 1: Cek Python ───────────────────────────────────────────────────
echo [1/4] Memeriksa Python...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo  [!] Python belum terinstall.
    echo      Membuka halaman download Python di browser...
    echo      Setelah install Python, CENTANG "Add Python to PATH",
    echo      lalu jalankan install.bat ini lagi.
    echo.
    start https://www.python.org/downloads/
    pause
    exit /b 1
) else (
    for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do (
        echo  [OK] Python %%v ditemukan.
    )
)

:: ─── LANGKAH 2: Cek pip ──────────────────────────────────────────────────────
echo.
echo [2/4] Memastikan pip tersedia...
python -m pip --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo  [!] pip tidak ditemukan. Mencoba menginstall pip...
    python -m ensurepip --upgrade
)
python -m pip install --upgrade pip --quiet
echo  [OK] pip siap.

:: ─── LANGKAH 3: Install dependencies ─────────────────────────────────────────
echo.
echo [3/4] Menginstall semua library yang dibutuhkan...
echo       (Proses ini mungkin memakan waktu 2-5 menit tergantung koneksi internet)
echo.
python -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo  [ERROR] Gagal menginstall library. Pastikan koneksi internet aktif.
    pause
    exit /b 1
)
echo.
echo  [OK] Semua library berhasil diinstall!

:: ─── LANGKAH 4: Buat start.bat portable ──────────────────────────────────────
echo.
echo [4/4] Menyiapkan shortcut untuk menjalankan aplikasi...

:: Tulis start.bat baru yang portable
(
echo @echo off
echo chcp 65001 ^>nul
echo title SnapTool
echo echo.
echo echo  Menghentikan server lama jika ada...
echo for /f "tokens=5" %%%%a in ^('netstat -aon ^| findstr ":8000"'^) do ^(
echo     taskkill /F /PID %%%%a ^>nul 2^>^&1
echo ^)
echo timeout /t 1 ^>nul
echo echo  Menjalankan SnapTool...
echo echo  Buka browser dan ketik: http://localhost:8000
echo echo  Tekan CTRL+C untuk menghentikan server.
echo echo.
echo start "" "http://localhost:8000"
echo python -m uvicorn main:app --host 0.0.0.0 --port 8000
echo pause
) > start.bat

echo  [OK] File start.bat siap digunakan.

:: ─── SELESAI ──────────────────────────────────────────────────────────────────
echo.
echo ============================================================
echo  INSTALASI SELESAI!
echo ============================================================
echo.
echo  Cara menjalankan SnapTool:
echo    ^> Klik dua kali file  start.bat
echo    ^> Browser akan terbuka otomatis ke http://localhost:8000
echo.
echo  Mau langsung jalankan sekarang? (Y/N)
set /p confirm=  Pilihan: 
if /i "%confirm%"=="Y" (
    echo.
    echo  Menjalankan SnapTool...
    start "" "http://localhost:8000"
    python -m uvicorn main:app --host 0.0.0.0 --port 8000
)

pause
