@echo off
setlocal
cd /d "%~dp0"
echo ==========================================
echo MatLex Desktop v11.3.1 Windows build
echo ==========================================
where node >nul 2>nul || (echo ERROR: Node.js 20+ is required.& pause & exit /b 1)
where python >nul 2>nul || (echo ERROR: Python 3.10+ is required.& pause & exit /b 1)

echo [1/4] Installing Python voice dependency...
python -m pip install edge-tts==7.2.8 || goto :fail

echo [2/4] Generating Microsoft Ava audio...
python tools\generate_desktop_audio.py || goto :fail

echo [3/4] Installing Electron build dependencies...
call npm install || goto :fail

echo [4/4] Building Windows installer and portable EXE...
call npm run dist:win || goto :fail

echo.
echo SUCCESS. Files are in the dist folder.
pause
exit /b 0

:fail
echo.
echo BUILD FAILED. Read the error above.
pause
exit /b 1
