@echo off
title Smart Cloud Cost Guardian - Backend API
cd /d "%~dp0"
echo ===================================================
echo  Starting Smart Cloud Cost Guardian Backend Engine
echo  API Documentation: http://localhost:8000/docs
echo ===================================================
if exist "%~dp0.venv\Scripts\python.exe" (
    "%~dp0.venv\Scripts\python.exe" -m uvicorn app.main:app --app-dir "%~dp0backend" --host 127.0.0.1 --port 8000
) else (
    python -m uvicorn app.main:app --app-dir "%~dp0backend" --host 127.0.0.1 --port 8000
)
pause
