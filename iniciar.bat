@echo off
chcp 65001 >nul
title Yarbis AI - Iniciando
cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] No esta instalado. Ejecuta primero: instalar.bat
    pause
    exit /b 1
)

if not exist "frontend\node_modules" (
    echo [ERROR] Frontend no instalado. Ejecuta: instalar.bat
    pause
    exit /b 1
)

if not exist ".env" (
    echo [AVISO] No hay .env. Copiando plantilla...
    copy /Y ".env.example" ".env" >nul
    echo Edita .env con tu GROQ_API_KEY antes de usar el chat.
)

echo.
echo  Iniciando Yarbis AI...
echo  Backend: http://127.0.0.1:8002
echo  Frontend: http://localhost:5173
echo.

:: Liberar puertos si quedaron procesos viejos
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8002.*LISTENING"') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173.*LISTENING"') do taskkill /F /PID %%a >nul 2>&1

:: Backend
start "Yarbis Backend" /min cmd /k ""%~dp0_run_backend.bat""

timeout /t 3 /nobreak >nul

:: Frontend
start "Yarbis Frontend" /min cmd /k ""%~dp0_run_frontend.bat""

timeout /t 5 /nobreak >nul

:: Abrir navegador
start "" "http://localhost:5173"

echo.
echo  Yarbis AI esta corriendo.
echo  Cierra las ventanas "Yarbis Backend" y "Yarbis Frontend" para detenerlo.
echo  O ejecuta: detener.bat
echo.
timeout /t 4 /nobreak >nul
