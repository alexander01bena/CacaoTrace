from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .database import db


CASCADE_ALL_DELETE_ORPHAN = "all, delete-orphan"
PRODUCTORES_FOREIGN_KEY = "productores.id"
FINCAS_FOREIGN_KEY = "fincas.id"
RECEPCIONES_FOREIGN_KEY = "recepciones.id"
LOTES_FOREIGN_KEY = "lotes.id"
DEFAULT_MUNICIPIO = "San Andrés de Tumaco"


class Role(db.Model):
    """Rol del usuario dentro del sistema."""

    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(150), nullable=True)

    users = db.relationship("User", back_populates="role")

    def __repr__(self):
        return f"<Role {self.name}>"


class User(UserMixin, db.Model):
    """Usuario que puede iniciar sesión en CacaoTrace."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active_user = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    role = db.relationship("Role", back_populates="users")

    @property
    def is_active(self):
        return self.is_active_user

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class Productor(db.Model):
    """Persona o familia que entrega cacao al centro de beneficio."""

    __tablename__ = "productores"

    id = db.Column(db.Integer, primary_key=True)
    nombres = db.Column(db.String(120), nullable=False)
    documento = db.Column(db.String(30), unique=True, nullable=True)
    telefono = db.Column(db.String(30), nullable=True)
    direccion = db.Column(db.String(150), nullable=True)
    municipio = db.Column(db.String(80), default=DEFAULT_MUNICIPIO)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    fincas = db.relationship(
        "Finca",
        back_populates="productor",
        cascade=CASCADE_ALL_DELETE_ORPHAN,
    )
    lotes = db.relationship("Lote", back_populates="productor")

    def __repr__(self):
        return f"<Productor {self.nombres}>"


class Finca(db.Model):
    """Finca o unidad productiva asociada a un productor."""

    __tablename__ = "fincas"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    vereda = db.Column(db.String(120), nullable=True)
    municipio = db.Column(db.String(80), default=DEFAULT_MUNICIPIO)
    hectareas = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    productor_id = db.Column(
        db.Integer,
        db.ForeignKey(PRODUCTORES_FOREIGN_KEY),
        nullable=False,
    )
    productor = db.relationship("Productor", back_populates="fincas")

    lotes = db.relationship("Lote", back_populates="finca")

    def __repr__(self):
        return f"<Finca {self.nombre}>"


class Recepcion(db.Model):
    """Entrada de cacao fresco o seco al centro de beneficio."""

    __tablename__ = "recepciones"

    id = db.Column(db.Integer, primary_key=True)
    tipo_cacao = db.Column(db.String(30), nullable=False)
    cantidad_kg = db.Column(db.Float, nullable=False)
    fecha_recepcion = db.Column(db.Date, nullable=False)
    observaciones = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    productor_id = db.Column(
        db.Integer,
        db.ForeignKey(PRODUCTORES_FOREIGN_KEY),
        nullable=False,
    )
    finca_id = db.Column(
        db.Integer,
        db.ForeignKey(FINCAS_FOREIGN_KEY),
        nullable=False,
    )

    productor = db.relationship("Productor")
    finca = db.relationship("Finca")
    lote = db.relationship("Lote", back_populates="recepcion", uselist=False)

    def __repr__(self):
        return f"<Recepcion {self.id} - {self.cantidad_kg} kg>"


class Lote(db.Model):
    """Lote trazable de cacao generado a partir de una recepción."""

    __tablename__ = "lotes"

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(30), unique=True, nullable=False)
    cantidad_inicial_kg = db.Column(db.Float, nullable=False)
    cantidad_actual_kg = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(40), default="Recepción")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    productor_id = db.Column(
        db.Integer,
        db.ForeignKey(PRODUCTORES_FOREIGN_KEY),
        nullable=False,
    )
    finca_id = db.Column(
        db.Integer,
        db.ForeignKey(FINCAS_FOREIGN_KEY),
        nullable=False,
    )
    recepcion_id = db.Column(
        db.Integer,
        db.ForeignKey(RECEPCIONES_FOREIGN_KEY),
        nullable=False,
    )

    productor = db.relationship("Productor", back_populates="lotes")
    finca = db.relationship("Finca", back_populates="lotes")
    recepcion = db.relationship("Recepcion", back_populates="lote")

    controles_calidad = db.relationship(
        "ControlCalidad",
        back_populates="lote",
        cascade=CASCADE_ALL_DELETE_ORPHAN,
    )
    procesos_poscosecha = db.relationship(
        "Poscosecha",
        back_populates="lote",
        cascade=CASCADE_ALL_DELETE_ORPHAN,
    )
    movimientos = db.relationship(
        "MovimientoInventario",
        back_populates="lote",
        cascade=CASCADE_ALL_DELETE_ORPHAN,
    )

    def __repr__(self):
        return f"<Lote {self.codigo}>"


class ControlCalidad(db.Model):
    """Registro de humedad, estado del grano y clasificación del lote."""

    __tablename__ = "controles_calidad"

    id = db.Column(db.Integer, primary_key=True)
    humedad = db.Column(db.Float, nullable=False)
    estado_grano = db.Column(db.String(60), nullable=False)
    clasificacion = db.Column(db.String(60), nullable=False)
    observaciones = db.Column(db.Text, nullable=True)
    fecha_control = db.Column(db.DateTime, default=datetime.utcnow)

    lote_id = db.Column(
        db.Integer,
        db.ForeignKey(LOTES_FOREIGN_KEY),
        nullable=False,
    )
    lote = db.relationship("Lote", back_populates="controles_calidad")

    def __repr__(self):
        return f"<ControlCalidad lote={self.lote_id}>"


class Poscosecha(db.Model):
    """Seguimiento del proceso de fermentación y secado del cacao."""

    __tablename__ = "poscosecha"

    id = db.Column(db.Integer, primary_key=True)
    fermentacion = db.Column(db.String(80), nullable=False)
    secado = db.Column(db.String(80), nullable=False)
    estado_proceso = db.Column(db.String(80), nullable=False)
    observaciones = db.Column(db.Text, nullable=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    lote_id = db.Column(
        db.Integer,
        db.ForeignKey(LOTES_FOREIGN_KEY),
        nullable=False,
    )
    lote = db.relationship("Lote", back_populates="procesos_poscosecha")

    def __repr__(self):
        return f"<Poscosecha lote={self.lote_id}>"


class MovimientoInventario(db.Model):
    """Entrada, salida o ajuste de la cantidad disponible de un lote."""

    __tablename__ = "movimientos_inventario"

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(30), nullable=False)
    cantidad_kg = db.Column(db.Float, nullable=False)
    motivo = db.Column(db.String(160), nullable=True)
    fecha_movimiento = db.Column(db.DateTime, default=datetime.utcnow)

    lote_id = db.Column(
        db.Integer,
        db.ForeignKey(LOTES_FOREIGN_KEY),
        nullable=False,
    )
    lote = db.relationship("Lote", back_populates="movimientos")

    def __repr__(self):
        return f"<Movimiento {self.tipo} {self.cantidad_kg} kg>"

