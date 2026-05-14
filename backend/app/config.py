from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    """Configuración principal de la aplicación."""

    SECRET_KEY = os.getenv("SECRET_KEY", "cambiar-esta-clave-en-produccion")

    # ============================================================
    # CONEXIÓN A MYSQL / XAMPP
    # ============================================================
    # Por defecto XAMPP usa:
    # usuario: root
    # contraseña: vacía
    # servidor: 127.0.0.1
    # puerto: 3306
    # base de datos: cacaotrace
    #
    # Si tu MySQL tiene contraseña, puedes cambiar MYSQL_PASSWORD
    # o editar directamente la variable SQLALCHEMY_DATABASE_URI.
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
    MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "cacaotrace")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
        f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(Config):
    """Configuración especial para ejecutar pruebas automáticas."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
