@echo off
chcp 65001 >nul
set "LINK=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Yarbis AI.lnk"

if exist "%LINK%" (
    del "%LINK%"
    echo Acceso directo de inicio automatico eliminado.
) else (
    echo No habia inicio automatico configurado.
)
timeout /t 2 /nobreak >nul
