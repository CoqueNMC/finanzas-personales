@echo off
title Finanzas Personales

:: Activar entorno virtual si tienes uno (opcional)
:: call .venv\Scripts\activate

:: Iniciar uvicorn en segundo plano
start "Backend Finanzas" cmd /k "cd /d %~dp0 && uvicorn backend.main:app --port 8000"

:: Esperar 3 segundos a que el servidor arranque
timeout /t 3 /nobreak > nul

:: Iniciar servidor del frontend en segundo plano
start "Frontend Finanzas" cmd /k "cd /d %~dp0\frontend && python -m http.server 3000"

:: Esperar 2 segundos más
timeout /t 2 /nobreak > nul

:: Abrir el navegador
start http://localhost:3000

echo Servidores iniciados. Cierra las ventanas de cmd para detenerlos.