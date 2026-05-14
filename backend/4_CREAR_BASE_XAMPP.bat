@echo off
chcp 65001 >nul
setlocal

REM ============================================================
REM  CacaoTrace Tumaco - Crear base de datos en XAMPP / MySQL
REM ============================================================

cd /d "%~dp0"

echo.
echo ============================================
echo  CREAR BASE DE DATOS EN XAMPP / MYSQL
echo ============================================
echo.
echo Antes de continuar, abre XAMPP y activa MySQL.
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
echo Creando/importando la base de datos cacaotrace...
python crear_base_xampp.py

if errorlevel 1 (
    echo.
    echo ERROR: No se pudo crear la base de datos.
    echo Revisa que MySQL este encendido en XAMPP.
    echo Si tu usuario root tiene contrasena, edita app\config.py o usa MYSQL_PASSWORD.
    pause
    exit /b 1
)

echo.
echo ============================================
echo  BASE DE DATOS LISTA
echo ============================================
echo Ahora ejecuta: 2_INICIAR_APP.bat
echo.
pause
