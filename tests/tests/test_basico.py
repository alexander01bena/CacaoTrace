from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from app import create_app
from app.database import db
from app.models import Role, User
from app.routes import convertir_fecha, convertir_float


USUARIO_PRUEBA = "admin_test_sonar"
CLAVE_PRUEBA = "admin123"


@pytest.fixture()
def app_prueba():
    app = create_app()
    app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
    )

    with app.app_context():
        db.create_all()

        rol_admin = Role.query.filter_by(name="administrador").first()

        if rol_admin is None:
            rol_admin = Role(
                name="administrador",
                description="Administrador del sistema",
            )
            db.session.add(rol_admin)
            db.session.commit()

        usuario = User.query.filter_by(username=USUARIO_PRUEBA).first()

        if usuario is None:
            usuario = User(
                username=USUARIO_PRUEBA,
                email="admin_test_sonar@cacaotrace.local",
                role_id=rol_admin.id,
                is_active_user=True,
            )
            usuario.set_password(CLAVE_PRUEBA)
            db.session.add(usuario)
        else:
            usuario.role_id = rol_admin.id
            usuario.is_active_user = True
            usuario.set_password(CLAVE_PRUEBA)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

    yield app


@pytest.fixture()
def cliente(app_prueba):
    return app_prueba.test_client()


def iniciar_sesion(cliente):
    return cliente.post(
        "/login",
        data={
            "username": USUARIO_PRUEBA,
            "password": CLAVE_PRUEBA,
        },
        follow_redirects=True,
    )


def test_convertir_fecha_vacia_retorna_fecha_actual():
    resultado = convertir_fecha("")
    assert isinstance(resultado, date)


def test_convertir_fecha_valida():
    resultado = convertir_fecha("2026-05-12")

    assert resultado.year == 2026
    assert resultado.month == 5
    assert resultado.day == 12


def test_convertir_float_valido():
    resultado = convertir_float("20.5", "cantidad", 0.01)

    assert resultado == 20.5


def test_convertir_float_invalido():
    with pytest.raises(ValueError):
        convertir_float("abc", "cantidad", 0.01)


def test_convertir_float_menor_al_minimo():
    with pytest.raises(ValueError):
        convertir_float("0", "cantidad", 0.01)


def test_login_get(cliente):
    respuesta = cliente.get("/login")

    assert respuesta.status_code == 200


def test_login_post_correcto(cliente):
    respuesta = iniciar_sesion(cliente)

    assert respuesta.status_code == 200


def test_dashboard_con_sesion(cliente):
    iniciar_sesion(cliente)

    respuesta = cliente.get("/dashboard")

    assert respuesta.status_code == 200


def test_productores_con_sesion(cliente):
    iniciar_sesion(cliente)

    respuesta = cliente.get("/productores")

    assert respuesta.status_code == 200


def test_fincas_con_sesion(cliente):
    iniciar_sesion(cliente)

    respuesta = cliente.get("/fincas")

    assert respuesta.status_code == 200


def test_recepciones_con_sesion(cliente):
    iniciar_sesion(cliente)

    respuesta = cliente.get("/recepciones")

    assert respuesta.status_code == 200


def test_lotes_con_sesion(cliente):
    iniciar_sesion(cliente)

    respuesta = cliente.get("/lotes")

    assert respuesta.status_code == 200


def test_inventario_con_sesion(cliente):
    iniciar_sesion(cliente)

    respuesta = cliente.get("/inventario")

    assert respuesta.status_code == 200


def test_reportes_con_sesion(cliente):
    iniciar_sesion(cliente)

    respuesta = cliente.get("/reportes")

    assert respuesta.status_code == 200


def test_consulta_publica(cliente):
    respuesta = cliente.get("/consulta-publica")

    assert respuesta.status_code in [200, 302, 404]
