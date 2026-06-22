@echo off
chcp 65001 >nul
title Yarbis AI - Instalacion
cd /d "%~dp0"

echo.
echo  ========================================
echo    YARBIS AI - Instalacion local
echo  ========================================
echo.

:: Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no encontrado.
    echo Instala Python 3.11+ desde https://www.python.org
    echo Marca "Add Python to PATH" durante la instalacion.
    pause
    exit /b 1
)

:: Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js no encontrado.
    echo Instala Node.js 20+ desde https://nodejs.org
    pause
    exit /b 1
)

echo [OK] Python y Node.js detectados.
echo.

:: Entorno virtual
if not exist "venv\Scripts\python.exe" (
    echo [1/4] Creando entorno virtual Python...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] No se pudo crear venv.
        pause
        exit /b 1
    )
) else (
    echo [1/4] Entorno virtual ya existe.
)

echo [2/4] Instalando dependencias Python...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip -q
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Fallo la instalacion de Python.
    pause
    exit /b 1
)

echo [3/4] Instalando dependencias Frontend...
cd frontend
call npm install
if errorlevel 1 (
    echo [ERROR] Fallo npm install.
    cd ..
    pause
    exit /b 1
)
cd ..

:: .env
if not exist ".env" (
    echo [4/4] Creando archivo .env desde plantilla...
    copy /Y ".env.example" ".env" >nul
    echo.
    echo  IMPORTANTE: Edita .env y pon tu GROQ_API_KEY
    echo  Obtener gratis en: https://console.groq.com
    echo.
) else (
    echo [4/4] Archivo .env ya existe.
)

echo.
echo  ========================================
echo    Instalacion completada
echo  ========================================
echo.
echo  Siguiente paso:
echo    1. Edita .env con tu API key de Groq
echo    2. Ejecuta iniciar.bat
echo.
echo  Modo sin internet (opcional):
echo    Instala Ollama desde https://ollama.com
echo    En .env pon: LLM_PROVIDER=ollama
echo    Luego: ollama pull llama3.2
echo.
pause
