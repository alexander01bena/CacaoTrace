from .database import db
from .models import Role, User


def crear_datos_iniciales():
    """Crea roles y usuario administrador si la base de datos está vacía."""

    roles_base = [
        ("administrador", "Gestiona usuarios, productores, fincas y reportes."),
        ("recepcion", "Registra entradas de cacao y creación de lotes."),
        ("calidad", "Registra controles de calidad y poscosecha."),
    ]

    for nombre, descripcion in roles_base:
        rol = Role.query.filter_by(name=nombre).first()
        if rol is None:
            db.session.add(Role(name=nombre, description=descripcion))

    db.session.commit()

    admin = User.query.filter_by(username="admin").first()
    if admin is None:
        rol_admin = Role.query.filter_by(name="administrador").first()
        admin = User(
            username="admin",
            email="admin@cacaotrace.local",
            role=rol_admin,
        )
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
