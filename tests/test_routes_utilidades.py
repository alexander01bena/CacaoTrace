from datetime import date

import pytest

from app.routes import convertir_fecha, convertir_float


def test_convertir_fecha_vacia():
    resultado = convertir_fecha("")
    assert isinstance(resultado, date)


def test_convertir_fecha_correcta():
    resultado = convertir_fecha("2026-05-12")
    assert resultado.year == 2026
    assert resultado.month == 5
    assert resultado.day == 12


def test_convertir_float_correcto():
    resultado = convertir_float("25.5", "cantidad", 0.01)
    assert resultado == 25.5


def test_convertir_float_invalido():
    with pytest.raises(ValueError):
        convertir_float("abc", "cantidad", 0.01)


def test_convertir_float_menor_al_minimo():
    with pytest.raises(ValueError):
        convertir_float("0", "cantidad", 0.01)


def test_convertir_float_negativo():
    with pytest.raises(ValueError):
        convertir_float("-5", "cantidad", 0.01)
