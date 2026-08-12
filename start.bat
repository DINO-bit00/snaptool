@echo off
chcp 65001 >nul
title SnapTool

echo.
echo  Menghentikan server lama jika ada...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000"') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 1 >nul

echo  Menjalankan SnapTool...
echo  Membuka browser ke http://localhost:8000
echo  Tekan CTRL+C untuk menghentikan server.
echo.

start "" "http://localhost:8000"
python -m uvicorn main:app --host 0.0.0.0 --port 8000
pause
