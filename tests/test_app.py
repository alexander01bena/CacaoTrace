from app import create_app
from app.config import TestingConfig
from app.database import db
from app.models import Productor, Finca, Recepcion, Lote, MovimientoInventario
from datetime import date


def crear_cliente_prueba():
    app = create_app(TestingConfig)
    app.config.update({"TESTING": True})
    cliente = app.test_client()
    return app, cliente


def login_admin(cliente):
    return cliente.post(
        "/login",
        data={"username": "admin", "password": "admin123"},
        follow_redirects=True,
    )


def test_login_admin_funciona():
    app, cliente = crear_cliente_prueba()
    with app.app_context():
        respuesta = login_admin(cliente)
        assert respuesta.status_code == 200
        assert b"Panel principal" in respuesta.data


def test_crear_productor_directamente_en_bd():
    app, cliente = crear_cliente_prueba()
    with app.app_context():
        productor = Productor(nombres="María Quiñones", documento="12345", telefono="3000000000")
        db.session.add(productor)
        db.session.commit()

        encontrado = Productor.query.filter_by(documento="12345").first()
        assert encontrado is not None
        assert encontrado.nombres == "María Quiñones"


def test_crear_lote_desde_recepcion():
    app, cliente = crear_cliente_prueba()
    with app.app_context():
        productor = Productor(nombres="Carlos Angulo", documento="9988")
        db.session.add(productor)
        db.session.flush()

        finca = Finca(nombre="La Esperanza", productor_id=productor.id, vereda="Zona rural")
        db.session.add(finca)
        db.session.flush()

        recepcion = Recepcion(
            productor_id=productor.id,
            finca_id=finca.id,
            tipo_cacao="Cacao seco",
            cantidad_kg=120,
            fecha_recepcion=date.today(),
        )
        db.session.add(recepcion)
        db.session.flush()

        lote = Lote(
            codigo="LOT-2026-0001",
            productor_id=productor.id,
            finca_id=finca.id,
            recepcion_id=recepcion.id,
            cantidad_inicial_kg=120,
            cantidad_actual_kg=120,
            estado="Recepción",
        )
        db.session.add(lote)
        db.session.flush()

        movimiento = MovimientoInventario(
            lote_id=lote.id,
            tipo="Entrada",
            cantidad_kg=120,
            motivo="Recepción inicial del lote",
        )
        db.session.add(movimiento)
        db.session.commit()

        assert Lote.query.count() == 1
        assert MovimientoInventario.query.count() == 1
        assert Lote.query.first().cantidad_actual_kg == 120
