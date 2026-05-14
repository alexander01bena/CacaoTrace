@echo off
chcp 65001 >nul
setlocal

REM ============================================================
REM  CacaoTrace Tumaco - Instalador automático para Windows
REM  Este archivo siempre trabaja desde la carpeta donde está guardado.
REM ============================================================

cd /d "%~dp0"

echo.
echo ============================================
echo  INSTALADOR DE CACAOTRACE TUMACO
echo ============================================
echo Carpeta del proyecto:
echo %cd%
echo.

REM Detectar Python. Primero intenta con py -3; si no existe, usa python.
py -3 --version >nul 2>&1
if %errorlevel%==0 (
    set "PYTHON_CMD=py -3"
) else (
    python --version >nul 2>&1
    if %errorlevel%==0 (
        set "PYTHON_CMD=python"
    ) else (
        echo ERROR: No se encontró Python instalado.
        echo Instala Python desde https://www.python.org/downloads/
        echo Marca la opción "Add Python to PATH" durante la instalación.
        pause
        exit /b 1
    )
)

echo Python detectado:
%PYTHON_CMD% --version
echo.

REM Crear entorno virtual si no existe.
if not exist "venv\Scripts\activate.bat" (
    echo Creando entorno virtual...
    %PYTHON_CMD% -m venv venv
    if errorlevel 1 (
        echo ERROR: No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
) else (
    echo El entorno virtual ya existe.
)

echo.
echo Activando entorno virtual...
call "venv\Scripts\activate.bat"

if errorlevel 1 (
    echo ERROR: No se pudo activar el entorno virtual.
    pause
    exit /b 1
)

echo.
echo Actualizando pip...
python -m pip install --upgrade pip

if errorlevel 1 (
    echo ERROR: No se pudo actualizar pip.
    pause
    exit /b 1
)

echo.
echo Instalando librerias del proyecto...
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: No se pudieron instalar las dependencias.
    echo Revisa tu conexion a internet o la instalacion de Python.
    pause
    exit /b 1
)

echo.
echo ============================================
echo  INSTALACION FINALIZADA CORRECTAMENTE
echo ============================================
echo Ahora ejecuta: 2_INICIAR_APP.bat
echo Usuario: admin
echo Contrasena: admin123
echo.
pause
