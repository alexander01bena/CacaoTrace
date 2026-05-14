"""
Script para crear/importar la base de datos CacaoTrace en MySQL de XAMPP.

Uso recomendado en Windows:
    4_CREAR_BASE_XAMPP.bat

También se puede ejecutar manualmente:
    python crear_base_xampp.py
"""

from pathlib import Path
import os
import sys
import pymysql

BASE_DIR = Path(__file__).resolve().parent
SQL_FILE = BASE_DIR / "cacaotrace_xampp_mysql.sql"

MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")


def dividir_sentencias_sql(sql_texto: str):
    """Divide el archivo SQL en sentencias sencillas separadas por punto y coma."""
    sentencias = []
    actual = []
    dentro_comilla = False
    comilla_actual = ""

    for linea in sql_texto.splitlines():
        linea_limpia = linea.strip()

        if not linea_limpia or linea_limpia.startswith("--"):
            continue

        for caracter in linea:
            if caracter in ("'", '"'):
                if not dentro_comilla:
                    dentro_comilla = True
                    comilla_actual = caracter
                elif comilla_actual == caracter:
                    dentro_comilla = False
                    comilla_actual = ""

            if caracter == ";" and not dentro_comilla:
                sentencia = "".join(actual).strip()
                if sentencia:
                    sentencias.append(sentencia)
                actual = []
            else:
                actual.append(caracter)
        actual.append("\n")

    sentencia_final = "".join(actual).strip()
    if sentencia_final:
        sentencias.append(sentencia_final)

    return sentencias


def main():
    if not SQL_FILE.exists():
        print(f"ERROR: No se encontró el archivo SQL: {SQL_FILE}")
        sys.exit(1)

    print("============================================")
    print(" CREANDO BASE DE DATOS CACAOTRACE EN XAMPP")
    print("============================================")
    print(f"Servidor MySQL: {MYSQL_HOST}:{MYSQL_PORT}")
    print(f"Usuario MySQL: {MYSQL_USER}")
    print(f"Archivo SQL: {SQL_FILE.name}")
    print()

    try:
        conexion = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            charset="utf8mb4",
            autocommit=True,
        )
    except Exception as error:
        print("ERROR: No se pudo conectar con MySQL de XAMPP.")
        print("Verifica que XAMPP tenga MySQL encendido.")
        print("Detalle del error:", error)
        sys.exit(1)

    sql_texto = SQL_FILE.read_text(encoding="utf-8")
    sentencias = dividir_sentencias_sql(sql_texto)

    try:
        with conexion.cursor() as cursor:
            for sentencia in sentencias:
                cursor.execute(sentencia)
    except Exception as error:
        print("ERROR: No se pudo ejecutar el script SQL completo.")
        print("Detalle del error:", error)
        sys.exit(1)
    finally:
        conexion.close()

    print("Base de datos creada correctamente.")
    print("Nombre de la base de datos: cacaotrace")
    print("Usuario inicial: admin")
    print("Contraseña inicial: admin123")


if __name__ == "__main__":
    main()
