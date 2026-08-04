@echo off
echo Stopping any existing SnapTool server on port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000"') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 1 >nul

echo Starting SnapTool server...
C:\Users\aryaa\AppData\Local\Python\pythoncore-3.14-64\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000
pause
