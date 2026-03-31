@echo off
echo ================================
echo   Starting WhatsApp AI Agent
echo ================================
echo.

echo [1/2] Starting Python backend...
start "Python Backend" cmd /k "cd /d C:\Users\M.Natafgi\whatsapp-agent\backend && venv\Scripts\activate && python main.py"

echo Waiting for Flask to start...
timeout /t 4 /nobreak > nul

echo [2/2] Starting WhatsApp bot...
start "WhatsApp Bot" cmd /k "cd /d C:\Users\M.Natafgi\whatsapp-agent\whatsapp && node index.js"

echo.
echo Both services started. Check the two new windows.
echo Close this window when done.
