@echo off
title Smart Cloud Cost Guardian - Frontend UI
cd /d "%~dp0frontend"
echo ===================================================
echo  Starting Smart Cloud Cost Guardian Frontend UI
echo  Frontend URL: http://localhost:5173
echo ===================================================
call npm run dev
pause
