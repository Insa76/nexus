@echo off
setlocal
cd /d "%~dp0"

where uv >nul 2>&1
if errorlevel 1 (
    echo ERROR: No se encontro uv en PATH.
    echo Instala uv o activa el entorno de desarrollo de NEXUS.
    pause
    exit /b 1
)

echo Iniciando runtime modular de NEXUS V1...
echo Servidor local: http://127.0.0.1:8765
echo Para detenerlo, presiona Ctrl+C.
uv run python -u server.py
set "NEXUS_EXIT=%ERRORLEVEL%"

if not "%NEXUS_EXIT%"=="0" (
    echo.
    echo NEXUS termino con codigo %NEXUS_EXIT%.
    pause
)
exit /b %NEXUS_EXIT%
