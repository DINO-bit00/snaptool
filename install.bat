@echo off
chcp 65001 >nul
title SnapTool - Installer
color 0A

echo.
echo  ============================================================
echo   SNAPTOOL - INSTALLER OTOMATIS
echo  ============================================================
echo.

:: ─── LANGKAH 1: Cari Python ──────────────────────────────────────────────────
echo  [1/3] Mencari Python di komputer Anda...

set PYTHON_EXE=

:: Cek "python" dulu
python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PY_VER=%%v
    set PYTHON_EXE=python
    echo        Ditemukan: python (versi %PY_VER%)
    goto :python_found
)

:: Cek "python3"
python3 --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    for /f "tokens=2 delims= " %%v in ('python3 --version 2^>^&1') do set PY_VER=%%v
    set PYTHON_EXE=python3
    echo        Ditemukan: python3 (versi %PY_VER%)
    goto :python_found
)

:: Cari di lokasi umum
for %%p in (
    "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    "C:\Python313\python.exe"
    "C:\Python312\python.exe"
    "C:\Python311\python.exe"
) do (
    if exist %%p (
        set PYTHON_EXE=%%~p
        echo        Ditemukan di: %%~p
        goto :python_found
    )
)

:: Python tidak ketemu
echo.
echo  [!] Python tidak ditemukan di komputer Anda!
echo.
echo      1. Buka browser dan pergi ke: https://www.python.org/downloads/
echo      2. Klik tombol "Download Python" (versi terbaru)
echo      3. Jalankan installer-nya
echo      4. PENTING: Centang kotak "Add Python to PATH"
echo      5. Setelah selesai, jalankan install.bat ini lagi
echo.
start https://www.python.org/downloads/
echo  Halaman download Python sudah dibuka di browser.
echo.
pause
exit /b 1

:python_found
echo  [OK] Python siap digunakan.

:: ─── LANGKAH 2: Install semua library ────────────────────────────────────────
echo.
echo  [2/3] Menginstall semua library yang dibutuhkan...
echo        Proses ini mungkin memakan waktu 2-10 menit.
echo        Mohon tunggu dan jangan tutup jendela ini.
echo.

"%PYTHON_EXE%" -m pip install --upgrade pip --quiet
"%PYTHON_EXE%" -m pip install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo  ============================================================
    echo  [ERROR] Gagal menginstall library!
    echo  ============================================================
    echo.
    echo  Kemungkinan penyebab:
    echo    - Koneksi internet tidak aktif atau lambat
    echo    - Antivirus memblokir proses instalasi
    echo.
    echo  Coba lagi setelah memastikan internet terhubung.
    echo.
    pause
    exit /b 1
)

:: ─── LANGKAH 3: Tulis start.bat dengan Python yang benar ─────────────────────
echo.
echo  [3/3] Menyimpan konfigurasi untuk start.bat...

(
echo @echo off
echo chcp 65001 ^>nul
echo title SnapTool
echo.
echo echo.
echo echo  ============================================================
echo echo   SNAPTOOL - Siap Digunakan!
echo echo  ============================================================
echo echo.
echo echo  Menghentikan server lama jika ada...
echo for /f "tokens=5" %%%%a in ^('netstat -aon ^| findstr ":8000"'^) do ^(
echo     taskkill /F /PID %%%%a ^>nul 2^>^&1
echo ^)
echo timeout /t 1 ^>nul
echo.
echo echo  Server berjalan. Browser akan terbuka sebentar lagi...
echo echo  Tekan CTRL+C di jendela ini untuk menghentikan server.
echo echo.
echo start "" "http://localhost:8000"
echo "%PYTHON_EXE%" -m uvicorn main:app --host 0.0.0.0 --port 8000
echo pause
) > start.bat

echo  [OK] start.bat berhasil dikonfigurasi!

:: ─── SELESAI ──────────────────────────────────────────────────────────────────
echo.
echo  ============================================================
echo   INSTALASI BERHASIL!
echo  ============================================================
echo.
echo  Cara menjalankan SnapTool selanjutnya:
echo    ^> Klik dua kali file  start.bat
echo    ^> Browser akan terbuka otomatis
echo.
set /p confirm= Mau langsung jalankan sekarang? (Y/N): 
if /i "%confirm%"=="Y" (
    echo.
    echo  Menjalankan SnapTool...
    start "" "http://localhost:8000"
    "%PYTHON_EXE%" -m uvicorn main:app --host 0.0.0.0 --port 8000
)

pause
