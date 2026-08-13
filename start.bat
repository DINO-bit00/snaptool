@echo off
title SnapTool

echo.
echo  ============================================================
echo   SNAPTOOL - Siap Digunakan!
echo  ============================================================
echo.
echo  Menghentikan server lama jika ada...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000"') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 1 >nul

echo  Server berjalan. Browser akan terbuka sebentar lagi...
echo  Tekan CTRL+C di jendela ini untuk menghentikan server.
echo.
start http://localhost:8000
call venv\Scripts\activate.bat
python -m uvicorn main:app --host 0.0.0.0 --port 8000
pause
