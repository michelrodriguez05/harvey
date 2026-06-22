@echo off
chcp 65001 >nul
title Yarbis AI - Inicio automatico
cd /d "%~dp0"

set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "LINK=%STARTUP%\Yarbis AI.lnk"
set "TARGET=%~dp0iniciar.bat"

if not exist "venv\Scripts\python.exe" (
    echo Ejecuta primero instalar.bat
    pause
    exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$s = (New-Object -ComObject WScript.Shell).CreateShortcut('%LINK%');" ^
  "$s.TargetPath = '%TARGET%';" ^
  "$s.WorkingDirectory = '%~dp0';" ^
  "$s.WindowStyle = 7;" ^
  "$s.Description = 'Iniciar Yarbis AI';" ^
  "$s.Save()"

if errorlevel 1 (
    echo [ERROR] No se pudo crear el acceso directo.
    pause
    exit /b 1
)

echo.
echo  Yarbis AI se iniciara automaticamente al encender Windows.
echo  Acceso directo creado en Inicio de Windows.
echo.
echo  Para quitarlo ejecuta: desinstalar-inicio-automatico.bat
echo.
pause
