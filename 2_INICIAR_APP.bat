@echo off
chcp 65001 >nul
setlocal

REM ============================================================
REM  CacaoTrace Tumaco - Inicio automático para Windows
REM  Versión conectada a MySQL de XAMPP.
REM ============================================================

cd /d "%~dp0"

echo.
echo ============================================
echo  INICIANDO CACAOTRACE TUMACO
echo ============================================
echo Carpeta del proyecto:
echo %cd%
echo.
echo IMPORTANTE: Antes de iniciar, abre XAMPP y activa MySQL.
echo Si aun no has creado la base de datos, ejecuta primero:
echo 4_CREAR_BASE_XAMPP.bat
echo.

REM Si no existe el entorno virtual, ejecuta el instalador primero.
if not exist "venv\Scripts\activate.bat" (
    echo No se encontro el entorno virtual.
    echo Se ejecutara la instalacion automaticamente.
    call "1_INSTALAR_TODO.bat"
)

call "venv\Scripts\activate.bat"

if errorlevel 1 (
    echo ERROR: No se pudo activar el entorno virtual.
    pause
    exit /b 1
)

echo.
echo Abriendo navegador en http://127.0.0.1:5000 ...
start "" "http://127.0.0.1:5000"

echo.
echo Si el navegador abre antes de que cargue la app, espera unos segundos y actualiza la pagina.
echo Para cerrar el sistema, vuelve a esta ventana y presiona CTRL + C.
echo.
python run.py

pause
