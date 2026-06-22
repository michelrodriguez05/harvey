@echo off
chcp 65001 >nul
title Yarbis AI - Detener
cd /d "%~dp0"

echo Deteniendo Yarbis AI...

taskkill /F /FI "WINDOWTITLE eq Yarbis Backend*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq Yarbis Frontend*" >nul 2>&1

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8002.*LISTENING"') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173.*LISTENING"') do taskkill /F /PID %%a >nul 2>&1

echo Listo. Yarbis AI detenido.
timeout /t 2 /nobreak >nul
