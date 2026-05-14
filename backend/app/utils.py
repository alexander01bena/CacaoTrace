from datetime import datetime
from .database import db
from .models import Lote


def generar_codigo_lote():
    """Genera un código único para cada lote usando el año actual y un consecutivo."""

    anio = datetime.now().year
    prefijo = f"LOT-{anio}-"

    total_lotes_anio = Lote.query.filter(Lote.codigo.like(f"{prefijo}%")).count()
    consecutivo = total_lotes_anio + 1

    return f"{prefijo}{consecutivo:04d}"


def guardar_cambios():
    """Centraliza el commit para facilitar mantenimiento y pruebas."""

    db.session.commit()
