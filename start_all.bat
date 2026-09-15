@echo off
title Smart Cloud Cost Guardian Launcher
cd /d "%~dp0"
echo ===================================================
echo  Launching Smart Cloud Cost Guardian Full Stack
echo ===================================================
echo Starting Backend API on http://localhost:8000 ...
start "SCCG Backend API" cmd /c "%~dp0start_backend.bat"
timeout /t 2 /nobreak >nul
echo Starting Frontend UI on http://localhost:5173 ...
start "SCCG Frontend UI" cmd /c "%~dp0start_frontend.bat"
echo.
echo Both services are starting in their respective windows!
echo Backend:  http://localhost:8000/docs
echo Frontend: http://localhost:5173
echo.
pause
