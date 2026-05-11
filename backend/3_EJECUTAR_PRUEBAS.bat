@echo off
chcp 65001 >nul
setlocal

REM ============================================================
REM  CacaoTrace Tumaco - Ejecutor de pruebas basicas
REM ============================================================

cd /d "%~dp0"

echo.
echo ============================================
echo  PRUEBAS BASICAS DE CACAOTRACE
echo ============================================
echo.

if not exist "venv\Scripts\activate.bat" (
    echo No se encontro el entorno virtual.
    echo Primero ejecuta 1_INSTALAR_TODO.bat
    pause
    exit /b 1
)

call "venv\Scripts\activate.bat"
pytest -q

echo.
pause
