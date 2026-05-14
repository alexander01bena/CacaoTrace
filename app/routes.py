from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import or_
from .database import db
from .decorators import roles_requeridos
from .models import (
    User,
    Role,
    Productor,
    Finca,
    Recepcion,
    Lote,
    ControlCalidad,
    Poscosecha,
    MovimientoInventario,
)
from .utils import generar_codigo_lote

main_bp = Blueprint("main", __name__)

DASHBOARD_ROUTE = "main.dashboard"
LOGIN_ROUTE = "main.login"
USUARIOS_ROUTE = "main.usuarios"
EDITAR_USUARIO_ROUTE = "main.editar_usuario"
PRODUCTORES_ROUTE = "main.productores"
EDITAR_PRODUCTOR_ROUTE = "main.editar_productor"
FINCAS_ROUTE = "main.fincas"
EDITAR_FINCA_ROUTE = "main.editar_finca"
RECEPCIONES_ROUTE = "main.recepciones"
EDITAR_RECEPCION_ROUTE = "main.editar_recepcion"
LOTES_ROUTE = "main.lotes"
DETALLE_LOTE_ROUTE = "main.detalle_lote"
EDITAR_LOTE_ROUTE = "main.editar_lote"
REGISTRAR_CALIDAD_ROUTE = "main.registrar_calidad"
EDITAR_CALIDAD_ROUTE = "main.editar_calidad"
REGISTRAR_POSCOSECHA_ROUTE = "main.registrar_poscosecha"
EDITAR_POSCOSECHA_ROUTE = "main.editar_poscosecha"
INVENTARIO_ROUTE = "main.inventario"
EDITAR_MOVIMIENTO_ROUTE = "main.editar_movimiento"
CONSULTAR_LOTE_ROUTE = "main.consultar_lote"

DEFAULT_MUNICIPIO = "San Andrés de Tumaco"
ESTADO_RECEPCION = "Recepción"
ESTADO_CALIDAD_REGISTRADA = "Calidad registrada"
ESTADO_FERMENTACION = "Fermentación"
ESTADO_SECADO = "Secado"
ESTADO_INVENTARIO = "Inventario"
ESTADO_VENDIDO = "Vendido"
ESTADO_AGOTADO = "Agotado"

TIPO_ENTRADA = "Entrada"
TIPO_SALIDA = "Salida"
TIPO_AJUSTE = "Ajuste"
MOTIVO_RECEPCION_INICIAL = "Recepción inicial del lote"

def convertir_fecha(valor):
    """Convierte una fecha recibida desde un input HTML a objeto date."""
    if not valor:
        return datetime.now().date()
    return datetime.strptime(valor, "%Y-%m-%d").date()

def convertir_float(valor, nombre_campo="valor", minimo=None):
    """Convierte un valor de formulario a número decimal y valida mínimos."""
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        raise ValueError(f"El campo {nombre_campo} debe ser numérico.")
    if minimo is not None and numero < minimo:
        raise ValueError(f"El campo {nombre_campo} debe ser mayor o igual que {minimo}.")
    return numero

def obtener_roles():
    return Role.query.order_by(Role.name.asc()).all()

def recalcular_cantidad_lote(lote):
    """Recalcula la cantidad actual de un lote a partir de sus movimientos."""
    cantidad = 0.0
    movimientos = MovimientoInventario.query.filter_by(lote_id=lote.id).order_by(
        MovimientoInventario.fecha_movimiento.asc(), MovimientoInventario.id.asc()
    ).all()

    for movimiento in movimientos:
        if movimiento.tipo == TIPO_ENTRADA:
            cantidad += movimiento.cantidad_kg
        elif movimiento.tipo == TIPO_SALIDA:
            cantidad -= movimiento.cantidad_kg
        elif movimiento.tipo == TIPO_AJUSTE:
            cantidad = movimiento.cantidad_kg

    lote.cantidad_actual_kg = max(cantidad, 0)
    if lote.cantidad_actual_kg == 0:
        lote.estado = ESTADO_AGOTADO
    elif lote.estado == ESTADO_AGOTADO and lote.cantidad_actual_kg > 0:
        lote.estado = ESTADO_INVENTARIO

@main_bp.app_errorhandler(403)
def error_403(error):
    return render_template(
        "error.html",
        titulo="Acceso no permitido",
        mensaje="No tienes permiso para entrar a esta sección."
    ), 403

@main_bp.app_errorhandler(404)
def error_404(error):
    return render_template(
        "error.html",
        titulo="Página no encontrada",
        mensaje="La página solicitada no existe."
    ), 404

@main_bp.route("/", methods=["GET"])
def index():
    if current_user.is_authenticated:
        return redirect(url_for(DASHBOARD_ROUTE))
    return redirect(url_for(LOGIN_ROUTE))

@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for(DASHBOARD_ROUTE))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password) and user.is_active:
            login_user(user)
            flash("Inicio de sesión correcto.", "success")
            return redirect(url_for(DASHBOARD_ROUTE))

        flash("Usuario o contraseña incorrectos.", "danger")

    return render_template("login.html")

@main_bp.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for(LOGIN_ROUTE))

@main_bp.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    resumen = {
        "productores": Productor.query.count(),
        "fincas": Finca.query.count(),
        "lotes": Lote.query.count(),
        "inventario_kg": db.session.query(
            db.func.coalesce(db.func.sum(Lote.cantidad_actual_kg), 0)
        ).scalar(),
    }
    ultimos_lotes = Lote.query.order_by(Lote.fecha_creacion.desc()).limit(5).all()
    return render_template("dashboard.html", resumen=resumen, ultimos_lotes=ultimos_lotes)

# -----------------------------------------------------------------------------
# USUARIOS
# -----------------------------------------------------------------------------
@main_bp.route("/usuarios", methods=["GET", "POST"])
@login_required
@roles_requeridos("administrador")
def usuarios():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        role_id = request.form.get("role_id")

        if not username or not email or not password or not role_id:
            flash("Todos los campos del usuario son obligatorios.", "warning")
            return redirect(url_for(USUARIOS_ROUTE))

        existe = User.query.filter(or_(User.username == username, User.email == email)).first()
        if existe:
            flash("Ya existe un usuario con ese nombre o correo.", "danger")
            return redirect(url_for(USUARIOS_ROUTE))

        usuario = User(username=username, email=email, role_id=int(role_id))
        usuario.set_password(password)
        db.session.add(usuario)
        db.session.commit()
        flash("Usuario creado correctamente.", "success")
        return redirect(url_for(USUARIOS_ROUTE))

    usuarios_registrados = User.query.order_by(User.created_at.desc()).all()
    return render_template("usuarios.html", usuarios=usuarios_registrados, roles=obtener_roles())

@main_bp.route("/usuarios/<int:usuario_id>/editar", methods=["GET", "POST"])
@login_required
@roles_requeridos("administrador")
def editar_usuario(usuario_id):
    usuario = User.query.get_or_404(usuario_id)

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        role_id = request.form.get("role_id")
        password = request.form.get("password", "").strip()
        is_active = request.form.get("is_active") == "on"

        if not username or not email or not role_id:
            flash("Usuario, correo y rol son obligatorios.", "warning")
            return redirect(url_for(EDITAR_USUARIO_ROUTE, usuario_id=usuario.id))

        duplicado = User.query.filter(
            User.id != usuario.id,
            or_(User.username == username, User.email == email),
        ).first()

        if duplicado:
            flash("Ya existe otro usuario con ese nombre o correo.", "danger")
            return redirect(url_for(EDITAR_USUARIO_ROUTE, usuario_id=usuario.id))

        usuario.username = username
        usuario.email = email
        usuario.role_id = int(role_id)
        usuario.is_active_user = is_active

        if password:
            usuario.set_password(password)

        db.session.commit()
        flash("Usuario actualizado correctamente.", "success")
        return redirect(url_for(USUARIOS_ROUTE))

    return render_template("editar_usuario.html", usuario=usuario, roles=obtener_roles())

@main_bp.route("/usuarios/<int:usuario_id>/eliminar", methods=["POST"])
@login_required
@roles_requeridos("administrador")
def eliminar_usuario(usuario_id):
    usuario = User.query.get_or_404(usuario_id)

    if usuario.id == current_user.id:
        flash("No puedes eliminar el usuario con el que estás conectado.", "warning")
        return redirect(url_for(USUARIOS_ROUTE))

    db.session.delete(usuario)
    db.session.commit()
    flash("Usuario eliminado correctamente.", "success")
    return redirect(url_for(USUARIOS_ROUTE))

# -----------------------------------------------------------------------------
# PRODUCTORES
# -----------------------------------------------------------------------------
@main_bp.route("/productores", methods=["GET", "POST"])
@login_required
@roles_requeridos("administrador", "recepcion")
def productores():
    if request.method == "POST":
        nombres = request.form.get("nombres", "").strip()
        documento = request.form.get("documento", "").strip() or None
        telefono = request.form.get("telefono", "").strip()
        direccion = request.form.get("direccion", "").strip()
        municipio = request.form.get("municipio", DEFAULT_MUNICIPIO).strip()

        if not nombres:
            flash("El nombre del productor es obligatorio.", "warning")
            return redirect(url_for(PRODUCTORES_ROUTE))

        if documento and Productor.query.filter_by(documento=documento).first():
            flash("Ya existe un productor con ese documento.", "danger")
            return redirect(url_for(PRODUCTORES_ROUTE))

        productor = Productor(
            nombres=nombres,
            documento=documento,
            telefono=telefono,
            direccion=direccion,
            municipio=municipio,
        )

        db.session.add(productor)
        db.session.commit()
        flash("Productor registrado correctamente.", "success")
        return redirect(url_for(PRODUCTORES_ROUTE))

    buscar = request.args.get("buscar", "").strip()
    consulta = Productor.query

    if buscar:
        consulta = consulta.filter(
            or_(
                Productor.nombres.ilike(f"%{buscar}%"),
                Productor.documento.ilike(f"%{buscar}%")
            )
        )

    productores_lista = consulta.order_by(Productor.created_at.desc()).all()
    return render_template("productores.html", productores=productores_lista, buscar=buscar)

@main_bp.route("/productores/<int:productor_id>/editar", methods=["GET", "POST"])
@login_required
@roles_requeridos("administrador", "recepcion")
def editar_productor(productor_id):
    productor = Productor.query.get_or_404(productor_id)

    if request.method == "POST":
        productor.nombres = request.form.get("nombres", "").strip()
        productor.documento = request.form.get("documento", "").strip() or None
        productor.telefono = request.form.get("telefono", "").strip()
        productor.direccion = request.form.get("direccion", "").strip()
        productor.municipio = request.form.get("municipio", DEFAULT_MUNICIPIO).strip()

        if not productor.nombres:
            flash("El nombre del productor no puede quedar vacío.", "warning")
            return redirect(url_for(EDITAR_PRODUCTOR_ROUTE, productor_id=productor.id))

        if productor.documento:
            duplicado = Productor.query.filter(
                Productor.id != productor.id,
                Productor.documento == productor.documento
            ).first()

            if duplicado:
                flash("Ya existe otro productor con ese documento.", "danger")
                return redirect(url_for(EDITAR_PRODUCTOR_ROUTE, productor_id=productor.id))

        db.session.commit()
        flash("Productor actualizado correctamente.", "success")
        return redirect(url_for(PRODUCTORES_ROUTE))

    return render_template("editar_productor.html", productor=productor)

@main_bp.route("/productores/<int:productor_id>/eliminar", methods=["POST"])
@login_required
@roles_requeridos("administrador")
def eliminar_productor(productor_id):
    productor = Productor.query.get_or_404(productor_id)

    try:
        # 1. Buscar las fincas asociadas al productor.
        fincas = Finca.query.filter_by(productor_id=productor.id).all()
        finca_ids = [finca.id for finca in fincas]

        # 2. Buscar todos los lotes asociados al productor.
        # También se buscan lotes asociados a sus fincas, para evitar datos sueltos.
        if finca_ids:
            lotes = Lote.query.filter(
                or_(
                    Lote.productor_id == productor.id,
                    Lote.finca_id.in_(finca_ids)
                )
            ).all()
        else:
            lotes = Lote.query.filter_by(productor_id=productor.id).all()

        lote_ids = [lote.id for lote in lotes]

        # 3. Eliminar primero los datos que dependen de los lotes.
        if lote_ids:
            MovimientoInventario.query.filter(
                MovimientoInventario.lote_id.in_(lote_ids)
            ).delete(synchronize_session=False)

            ControlCalidad.query.filter(
                ControlCalidad.lote_id.in_(lote_ids)
            ).delete(synchronize_session=False)

            Poscosecha.query.filter(
                Poscosecha.lote_id.in_(lote_ids)
            ).delete(synchronize_session=False)

            # 4. Eliminar los lotes.
            Lote.query.filter(
                Lote.id.in_(lote_ids)
            ).delete(synchronize_session=False)

        # 5. Eliminar recepciones asociadas al productor o a sus fincas.
        if finca_ids:
            Recepcion.query.filter(
                or_(
                    Recepcion.productor_id == productor.id,
                    Recepcion.finca_id.in_(finca_ids)
                )
            ).delete(synchronize_session=False)
        else:
            Recepcion.query.filter_by(
                productor_id=productor.id
            ).delete(synchronize_session=False)

        # 6. Eliminar fincas del productor.
        Finca.query.filter_by(
            productor_id=productor.id
        ).delete(synchronize_session=False)

        # 7. Eliminar finalmente el productor.
        db.session.delete(productor)

        db.session.commit()

        flash(
            "Productor eliminado correctamente junto con sus fincas, recepciones, lotes, calidad, poscosecha e inventario asociados.",
            "success"
        )

    except Exception as error:
        db.session.rollback()
        flash(f"No se pudo eliminar el productor. Error: {str(error)}", "danger")

    return redirect(url_for(PRODUCTORES_ROUTE))

# -----------------------------------------------------------------------------
# FINCAS
# -----------------------------------------------------------------------------
@main_bp.route("/fincas", methods=["GET", "POST"])
@login_required
@roles_requeridos("administrador", "recepcion")
def fincas():
    productores_lista = Productor.query.order_by(Productor.nombres.asc()).all()

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        vereda = request.form.get("vereda", "").strip()
        municipio = request.form.get("municipio", DEFAULT_MUNICIPIO).strip()
        hectareas = request.form.get("hectareas") or None
        productor_id = request.form.get("productor_id")

        if not nombre or not productor_id:
            flash("El nombre de la finca y el productor son obligatorios.", "warning")
            return redirect(url_for(FINCAS_ROUTE))

        finca = Finca(
            nombre=nombre,
            vereda=vereda,
            municipio=municipio,
            hectareas=float(hectareas) if hectareas else None,
            productor_id=int(productor_id),
        )

        db.session.add(finca)
        db.session.commit()
        flash("Finca registrada correctamente.", "success")
        return redirect(url_for(FINCAS_ROUTE))

    fincas_lista = Finca.query.order_by(Finca.created_at.desc()).all()
    return render_template("fincas.html", fincas=fincas_lista, productores=productores_lista)

@main_bp.route("/fincas/<int:finca_id>/editar", methods=["GET", "POST"])
@login_required
@roles_requeridos("administrador", "recepcion")
def editar_finca(finca_id):
    finca = Finca.query.get_or_404(finca_id)
    productores_lista = Productor.query.order_by(Productor.nombres.asc()).all()

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        productor_id = request.form.get("productor_id")
        vereda = request.form.get("vereda", "").strip()
        municipio = request.form.get("municipio", DEFAULT_MUNICIPIO).strip()
        hectareas = request.form.get("hectareas") or None

        if not nombre or not productor_id:
            flash("El nombre de la finca y el productor son obligatorios.", "warning")
            return redirect(url_for(EDITAR_FINCA_ROUTE, finca_id=finca.id))

        finca.nombre = nombre
        finca.productor_id = int(productor_id)
        finca.vereda = vereda
        finca.municipio = municipio
        finca.hectareas = float(hectareas) if hectareas else None

        db.session.commit()
        flash("Finca actualizada correctamente.", "success")
        return redirect(url_for(FINCAS_ROUTE))

    return render_template("editar_finca.html", finca=finca, productores=productores_lista)

@main_bp.route("/fincas/<int:finca_id>/eliminar", methods=["POST"])
@login_required
@roles_requeridos("administrador")
def eliminar_finca(finca_id):
    finca = Finca.query.get_or_404(finca_id)
    tiene_lotes = Lote.query.filter_by(finca_id=finca.id).first() is not None
    tiene_recepciones = Recepcion.query.filter_by(finca_id=finca.id).first() is not None

    if tiene_lotes or tiene_recepciones:
        flash("No se puede eliminar la finca porque tiene recepciones o lotes asociados.", "warning")
        return redirect(url_for(FINCAS_ROUTE))

    db.session.delete(finca)
    db.session.commit()
    flash("Finca eliminada correctamente.", "success")
    return redirect(url_for(FINCAS_ROUTE))

# -----------------------------------------------------------------------------
# RECEPCIONES Y LOTES
# -----------------------------------------------------------------------------
@main_bp.route("/recepciones", methods=["GET", "POST"])
@login_required
@roles_requeridos("administrador", "recepcion")
def recepciones():
    productores_lista = Productor.query.order_by(Productor.nombres.asc()).all()
    fincas_lista = Finca.query.order_by(Finca.nombre.asc()).all()

    if request.method == "POST":
        productor_id = request.form.get("productor_id")
        finca_id = request.form.get("finca_id")
        tipo_cacao = request.form.get("tipo_cacao", "").strip()
        cantidad_kg = request.form.get("cantidad_kg")
        fecha_recepcion = convertir_fecha(request.form.get("fecha_recepcion"))
        observaciones = request.form.get("observaciones", "").strip()

        if not productor_id or not finca_id or not tipo_cacao or not cantidad_kg:
            flash("Productor, finca, tipo de cacao y cantidad son obligatorios.", "warning")
            return redirect(url_for(RECEPCIONES_ROUTE))

        try:
            cantidad = convertir_float(cantidad_kg, "cantidad", 0.01)
        except ValueError as error:
            flash(str(error), "warning")
            return redirect(url_for(RECEPCIONES_ROUTE))

        recepcion = Recepcion(
            productor_id=int(productor_id),
            finca_id=int(finca_id),
            tipo_cacao=tipo_cacao,
            cantidad_kg=cantidad,
            fecha_recepcion=fecha_recepcion,
            observaciones=observaciones,
        )

        db.session.add(recepcion)
        db.session.flush()

        lote = Lote(
            codigo=generar_codigo_lote(),
            productor_id=int(productor_id),
            finca_id=int(finca_id),
            recepcion_id=recepcion.id,
            cantidad_inicial_kg=cantidad,
            cantidad_actual_kg=cantidad,
            estado=ESTADO_RECEPCION,
        )

        db.session.add(lote)
        db.session.flush()

        movimiento = MovimientoInventario(
            lote_id=lote.id,
            tipo=TIPO_ENTRADA,
            cantidad_kg=cantidad,
            motivo=MOTIVO_RECEPCION_INICIAL,
        )

        db.session.add(movimiento)
        db.session.commit()

        flash(f"Recepción registrada. Se creó el lote {lote.codigo}.", "success")
        return redirect(url_for(DETALLE_LOTE_ROUTE, lote_id=lote.id))

    recepciones_lista = Recepcion.query.order_by(Recepcion.created_at.desc()).all()

    return render_template(
        "recepciones.html",
        recepciones=recepciones_lista,
        productores=productores_lista,
        fincas=fincas_lista,
    )

@main_bp.route("/recepciones/<int:recepcion_id>/editar", methods=["GET", "POST"])
@login_required
@roles_requeridos("administrador", "recepcion")
def editar_recepcion(recepcion_id):
    recepcion = Recepcion.query.get_or_404(recepcion_id)
    productores_lista = Productor.query.order_by(Productor.nombres.asc()).all()
    fincas_lista = Finca.query.order_by(Finca.nombre.asc()).all()

    if request.method == "POST":
        productor_id = request.form.get("productor_id")
        finca_id = request.form.get("finca_id")
        tipo_cacao = request.form.get("tipo_cacao", "").strip()
        cantidad_kg = request.form.get("cantidad_kg")
        fecha_recepcion = convertir_fecha(request.form.get("fecha_recepcion"))
        observaciones = request.form.get("observaciones", "").strip()

        if not productor_id or not finca_id or not tipo_cacao or not cantidad_kg:
            flash("Productor, finca, tipo y cantidad son obligatorios.", "warning")
            return redirect(url_for(EDITAR_RECEPCION_ROUTE, recepcion_id=recepcion.id))

        try:
            nueva_cantidad = convertir_float(cantidad_kg, "cantidad", 0.01)
        except ValueError as error:
            flash(str(error), "warning")
            return redirect(url_for(EDITAR_RECEPCION_ROUTE, recepcion_id=recepcion.id))

        lote = recepcion.lote
        diferencia = nueva_cantidad - recepcion.cantidad_kg

        if lote and lote.cantidad_actual_kg + diferencia < 0:
            flash("No se puede reducir la recepción porque la cantidad actual del lote quedaría negativa.", "danger")
            return redirect(url_for(EDITAR_RECEPCION_ROUTE, recepcion_id=recepcion.id))

        recepcion.productor_id = int(productor_id)
        recepcion.finca_id = int(finca_id)
        recepcion.tipo_cacao = tipo_cacao
        recepcion.cantidad_kg = nueva_cantidad
        recepcion.fecha_recepcion = fecha_recepcion
        recepcion.observaciones = observaciones

        if lote:
            lote.productor_id = int(productor_id)
            lote.finca_id = int(finca_id)
            lote.cantidad_inicial_kg = nueva_cantidad
            lote.cantidad_actual_kg += diferencia

            movimiento_inicial = MovimientoInventario.query.filter_by(
                lote_id=lote.id,
                tipo=TIPO_ENTRADA,
                motivo=MOTIVO_RECEPCION_INICIAL,
            ).first()

            if movimiento_inicial:
                movimiento_inicial.cantidad_kg = nueva_cantidad
                recalcular_cantidad_lote(lote)

        db.session.commit()
        flash("Recepción actualizada correctamente.", "success")
        return redirect(url_for(RECEPCIONES_ROUTE))

    return render_template(
        "editar_recepcion.html",
        recepcion=recepcion,
        productores=productores_lista,
        fincas=fincas_lista
    )

@main_bp.route("/recepciones/<int:recepcion_id>/eliminar", methods=["POST"])
@login_required
@roles_requeridos("administrador")
def eliminar_recepcion(recepcion_id):
    recepcion = Recepcion.query.get_or_404(recepcion_id)
    lote = recepcion.lote

    if lote:
        db.session.delete(lote)
        db.session.flush()

    db.session.delete(recepcion)
    db.session.commit()
    flash("Recepción y lote asociado eliminados correctamente.", "success")
    return redirect(url_for(RECEPCIONES_ROUTE))

@main_bp.route("/lotes", methods=["GET"])
@login_required
def lotes():
    buscar = request.args.get("buscar", "").strip()
    estado = request.args.get("estado", "").strip()

    consulta = Lote.query

    if buscar:
        consulta = consulta.filter(Lote.codigo.ilike(f"%{buscar}%"))

    if estado:
        consulta = consulta.filter_by(estado=estado)

    lotes_lista = consulta.order_by(Lote.fecha_creacion.desc()).all()
    estados = [fila[0] for fila in db.session.query(Lote.estado).distinct().all()]

    return render_template(
        "lotes.html",
        lotes=lotes_lista,
        buscar=buscar,
        estado=estado,
        estados=estados
    )

@main_bp.route("/lotes/<int:lote_id>", methods=["GET"])
@login_required
def detalle_lote(lote_id):
    lote = Lote.query.get_or_404(lote_id)
    return render_template("detalle_lote.html", lote=lote)

@main_bp.route("/lotes/<int:lote_id>/editar", methods=["GET", "POST"])
@login_required
@roles_requeridos("administrador", "recepcion", "calidad")
def editar_lote(lote_id):
    lote = Lote.query.get_or_404(lote_id)
    productores_lista = Productor.query.order_by(Productor.nombres.asc()).all()
    fincas_lista = Finca.query.order_by(Finca.nombre.asc()).all()
    estados = [
        ESTADO_RECEPCION,
        ESTADO_CALIDAD_REGISTRADA,
        ESTADO_FERMENTACION,
        ESTADO_SECADO,
        ESTADO_INVENTARIO,
        ESTADO_VENDIDO,
        ESTADO_AGOTADO
    ]

    if request.method == "POST":
        productor_id = request.form.get("productor_id")
        finca_id = request.form.get("finca_id")
        estado = request.form.get("estado", "").strip()
        cantidad_inicial = request.form.get("cantidad_inicial_kg")
        cantidad_actual = request.form.get("cantidad_actual_kg")

        try:
            inicial = convertir_float(cantidad_inicial, "cantidad inicial", 0)
            actual = convertir_float(cantidad_actual, "cantidad actual", 0)
        except ValueError as error:
            flash(str(error), "warning")
            return redirect(url_for(EDITAR_LOTE_ROUTE, lote_id=lote.id))

        if not productor_id or not finca_id or not estado:
            flash("Productor, finca y estado son obligatorios.", "warning")
            return redirect(url_for(EDITAR_LOTE_ROUTE, lote_id=lote.id))

        lote.productor_id = int(productor_id)
        lote.finca_id = int(finca_id)
        lote.estado = estado
        lote.cantidad_inicial_kg = inicial
        lote.cantidad_actual_kg = actual

        if lote.recepcion:
            lote.recepcion.productor_id = int(productor_id)
            lote.recepcion.finca_id = int(finca_id)
            lote.recepcion.cantidad_kg = inicial

        db.session.commit()
        flash("Lote actualizado correctamente.", "success")
        return redirect(url_for(DETALLE_LOTE_ROUTE, lote_id=lote.id))

    return render_template(
        "editar_lote.html",
        lote=lote,
        productores=productores_lista,
        fincas=fincas_lista,
        estados=estados
    )

@main_bp.route("/lotes/<int:lote_id>/eliminar", methods=["POST"])
@login_required
@roles_requeridos("administrador")
def eliminar_lote(lote_id):
    lote = Lote.query.get_or_404(lote_id)
    recepcion = lote.recepcion

    db.session.delete(lote)
    db.session.flush()

    if recepcion:
        db.session.delete(recepcion)

    db.session.commit()
    flash("Lote y recepción asociada eliminados correctamente.", "success")
    return redirect(url_for(LOTES_ROUTE))

# -----------------------------------------------------------------------------
# CALIDAD Y POSCOSECHA
# -----------------------------------------------------------------------------
@main_bp.route("/calidad/<int:lote_id>", methods=["GET", "POST"])
@login_required
@roles_requeridos("administrador", "calidad")
def registrar_calidad(lote_id):
    lote = Lote.query.get_or_404(lote_id)

    if request.method == "POST":
        humedad = request.form.get("humedad")
        estado_grano = request.form.get("estado_grano", "").strip()
        clasificacion = request.form.get("clasificacion", "").strip()
        observaciones = request.form.get("observaciones", "").strip()

        if not humedad or not estado_grano or not clasificacion:
            flash("Humedad, estado del grano y clasificación son obligatorios.", "warning")
            return redirect(url_for(REGISTRAR_CALIDAD_ROUTE, lote_id=lote.id))

        control = ControlCalidad(
            lote_id=lote.id,
            humedad=float(humedad),
            estado_grano=estado_grano,
            clasificacion=clasificacion,
            observaciones=observaciones,
        )

        lote.estado = ESTADO_CALIDAD_REGISTRADA
        db.session.add(control)
        db.session.commit()
        flash("Control de calidad registrado correctamente.", "success")
        return redirect(url_for(DETALLE_LOTE_ROUTE, lote_id=lote.id))

    return render_template("calidad_form.html", lote=lote, control=None)

@main_bp.route("/calidad/registro/<int:control_id>/editar", methods=["GET", "POST"])
@login_required
@roles_requeridos("administrador", "calidad")
def editar_calidad(control_id):
    control = ControlCalidad.query.get_or_404(control_id)
    lote = control.lote

    if request.method == "POST":
        humedad = request.form.get("humedad")
        estado_grano = request.form.get("estado_grano", "").strip()
        clasificacion = request.form.get("clasificacion", "").strip()
        observaciones = request.form.get("observaciones", "").strip()

        if not humedad or not estado_grano or not clasificacion:
            flash("Humedad, estado del grano y clasificación son obligatorios.", "warning")
            return redirect(url_for(EDITAR_CALIDAD_ROUTE, control_id=control.id))

        control.humedad = float(humedad)
        control.estado_grano = estado_grano
        control.clasificacion = clasificacion
        control.observaciones = observaciones

        db.session.commit()
        flash("Control de calidad actualizado correctamente.", "success")
        return redirect(url_for(DETALLE_LOTE_ROUTE, lote_id=lote.id))

    return render_template("calidad_form.html", lote=lote, control=control)

@main_bp.route("/calidad/registro/<int:control_id>/eliminar", methods=["POST"])
@login_required
@roles_requeridos("administrador")
def eliminar_calidad(control_id):
    control = ControlCalidad.query.get_or_404(control_id)
    lote_id = control.lote_id

    db.session.delete(control)
    db.session.commit()

    flash("Control de calidad eliminado correctamente.", "success")
    return redirect(url_for(DETALLE_LOTE_ROUTE, lote_id=lote_id))

@main_bp.route("/poscosecha/<int:lote_id>", methods=["GET", "POST"])
@login_required
@roles_requeridos("administrador", "calidad")
def registrar_poscosecha(lote_id):
    lote = Lote.query.get_or_404(lote_id)

    if request.method == "POST":
        fermentacion = request.form.get("fermentacion", "").strip()
        secado = request.form.get("secado", "").strip()
        estado_proceso = request.form.get("estado_proceso", "").strip()
        observaciones = request.form.get("observaciones", "").strip()

        if not fermentacion or not secado or not estado_proceso:
            flash("Fermentación, secado y estado del proceso son obligatorios.", "warning")
            return redirect(url_for(REGISTRAR_POSCOSECHA_ROUTE, lote_id=lote.id))

        proceso = Poscosecha(
            lote_id=lote.id,
            fermentacion=fermentacion,
            secado=secado,
            estado_proceso=estado_proceso,
            observaciones=observaciones,
        )

        lote.estado = estado_proceso
        db.session.add(proceso)
        db.session.commit()

        flash("Proceso poscosecha registrado correctamente.", "success")
        return redirect(url_for(DETALLE_LOTE_ROUTE, lote_id=lote.id))

    return render_template("poscosecha_form.html", lote=lote, proceso=None)

@main_bp.route("/poscosecha/registro/<int:proceso_id>/editar", methods=["GET", "POST"])
@login_required
@roles_requeridos("administrador", "calidad")
def editar_poscosecha(proceso_id):
    proceso = Poscosecha.query.get_or_404(proceso_id)
    lote = proceso.lote

    if request.method == "POST":
        fermentacion = request.form.get("fermentacion", "").strip()
        secado = request.form.get("secado", "").strip()
        estado_proceso = request.form.get("estado_proceso", "").strip()
        observaciones = request.form.get("observaciones", "").strip()

        if not fermentacion or not secado or not estado_proceso:
            flash("Fermentación, secado y estado del proceso son obligatorios.", "warning")
            return redirect(url_for(EDITAR_POSCOSECHA_ROUTE, proceso_id=proceso.id))

        proceso.fermentacion = fermentacion
        proceso.secado = secado
        proceso.estado_proceso = estado_proceso
        proceso.observaciones = observaciones
        lote.estado = estado_proceso

        db.session.commit()
        flash("Proceso poscosecha actualizado correctamente.", "success")
        return redirect(url_for(DETALLE_LOTE_ROUTE, lote_id=lote.id))

    return render_template("poscosecha_form.html", lote=lote, proceso=proceso)

@main_bp.route("/poscosecha/registro/<int:proceso_id>/eliminar", methods=["POST"])
@login_required
@roles_requeridos("administrador")
def eliminar_poscosecha(proceso_id):
    proceso = Poscosecha.query.get_or_404(proceso_id)
    lote_id = proceso.lote_id

    db.session.delete(proceso)
    db.session.commit()

    flash("Proceso poscosecha eliminado correctamente.", "success")
    return redirect(url_for(DETALLE_LOTE_ROUTE, lote_id=lote_id))

# -----------------------------------------------------------------------------
# INVENTARIO
# -----------------------------------------------------------------------------
@main_bp.route("/inventario", methods=["GET", "POST"])
@login_required
@roles_requeridos("administrador", "recepcion", "calidad")
def inventario():
    if request.method == "POST":
        lote_id = request.form.get("lote_id")
        tipo = request.form.get("tipo", "").strip()
        cantidad_kg = request.form.get("cantidad_kg")
        motivo = request.form.get("motivo", "").strip()

        lote = Lote.query.get_or_404(int(lote_id))

        try:
            cantidad = convertir_float(cantidad_kg, "cantidad", 0.01)
        except ValueError as error:
            flash(str(error), "warning")
            return redirect(url_for(INVENTARIO_ROUTE))

        if tipo == TIPO_SALIDA and cantidad > lote.cantidad_actual_kg:
            flash("La salida no puede superar la cantidad disponible del lote.", "danger")
            return redirect(url_for(INVENTARIO_ROUTE))

        if tipo not in [TIPO_ENTRADA, TIPO_SALIDA, TIPO_AJUSTE]:
            flash("Tipo de movimiento no válido.", "danger")
            return redirect(url_for(INVENTARIO_ROUTE))

        movimiento = MovimientoInventario(
            lote_id=lote.id,
            tipo=tipo,
            cantidad_kg=cantidad,
            motivo=motivo
        )

        db.session.add(movimiento)
        db.session.flush()

        recalcular_cantidad_lote(lote)

        if tipo in [TIPO_ENTRADA, TIPO_AJUSTE] and lote.cantidad_actual_kg > 0:
            lote.estado = ESTADO_INVENTARIO

        db.session.commit()
        flash("Movimiento de inventario registrado.", "success")
        return redirect(url_for(INVENTARIO_ROUTE))

    lotes_lista = Lote.query.order_by(Lote.fecha_creacion.desc()).all()
    movimientos = MovimientoInventario.query.order_by(
        MovimientoInventario.fecha_movimiento.desc()
    ).limit(20).all()

    return render_template("inventario.html", lotes=lotes_lista, movimientos=movimientos)

@main_bp.route("/inventario/movimiento/<int:movimiento_id>/editar", methods=["GET", "POST"])
@login_required
@roles_requeridos("administrador", "recepcion", "calidad")
def editar_movimiento(movimiento_id):
    movimiento = MovimientoInventario.query.get_or_404(movimiento_id)
    lote = movimiento.lote

    if request.method == "POST":
        tipo = request.form.get("tipo", "").strip()
        cantidad_kg = request.form.get("cantidad_kg")
        motivo = request.form.get("motivo", "").strip()

        if tipo not in [TIPO_ENTRADA, TIPO_SALIDA, TIPO_AJUSTE]:
            flash("Tipo de movimiento no válido.", "danger")
            return redirect(url_for(EDITAR_MOVIMIENTO_ROUTE, movimiento_id=movimiento.id))

        try:
            cantidad = convertir_float(cantidad_kg, "cantidad", 0.01)
        except ValueError as error:
            flash(str(error), "warning")
            return redirect(url_for(EDITAR_MOVIMIENTO_ROUTE, movimiento_id=movimiento.id))

        movimiento.tipo = tipo
        movimiento.cantidad_kg = cantidad
        movimiento.motivo = motivo

        recalcular_cantidad_lote(lote)
        db.session.commit()

        flash("Movimiento actualizado correctamente.", "success")
        return redirect(url_for(INVENTARIO_ROUTE))

    return render_template("editar_movimiento.html", movimiento=movimiento)

@main_bp.route("/inventario/movimiento/<int:movimiento_id>/eliminar", methods=["POST"])
@login_required
@roles_requeridos("administrador")
def eliminar_movimiento(movimiento_id):
    movimiento = MovimientoInventario.query.get_or_404(movimiento_id)
    lote = movimiento.lote

    db.session.delete(movimiento)
    db.session.flush()

    recalcular_cantidad_lote(lote)

    db.session.commit()
    flash("Movimiento eliminado correctamente.", "success")
    return redirect(url_for(INVENTARIO_ROUTE))

# -----------------------------------------------------------------------------
# REPORTES Y CONSULTA PÚBLICA
# -----------------------------------------------------------------------------
@main_bp.route("/reportes", methods=["GET"])
@login_required
@roles_requeridos("administrador")
def reportes():
    productor_id = request.args.get("productor_id", "")
    estado = request.args.get("estado", "")
    clasificacion = request.args.get("clasificacion", "")
    fecha_inicio = request.args.get("fecha_inicio", "")
    fecha_fin = request.args.get("fecha_fin", "")

    consulta = Lote.query

    if productor_id:
        consulta = consulta.filter(Lote.productor_id == int(productor_id))

    if estado:
        consulta = consulta.filter(Lote.estado == estado)

    if fecha_inicio:
        consulta = consulta.filter(
            Lote.fecha_creacion >= datetime.strptime(fecha_inicio, "%Y-%m-%d")
        )

    if fecha_fin:
        fecha_fin_dt = datetime.strptime(fecha_fin, "%Y-%m-%d")
        consulta = consulta.filter(Lote.fecha_creacion <= fecha_fin_dt)

    lotes_resultado = consulta.order_by(Lote.fecha_creacion.desc()).all()

    if clasificacion:
        lotes_resultado = [
            lote for lote in lotes_resultado
            if lote.controles_calidad and lote.controles_calidad[-1].clasificacion == clasificacion
        ]

    total_kg = sum(lote.cantidad_actual_kg for lote in lotes_resultado)
    productores_lista = Productor.query.order_by(Productor.nombres.asc()).all()
    estados = [fila[0] for fila in db.session.query(Lote.estado).distinct().all()]
    clasificaciones = ["Calidad alta", "Calidad media", "Calidad baja", "Rechazado"]

    return render_template(
        "reportes.html",
        lotes=lotes_resultado,
        productores=productores_lista,
        estados=estados,
        clasificaciones=clasificaciones,
        total_kg=total_kg,
        filtros=request.args,
    )

@main_bp.route("/consultar-lote", methods=["GET", "POST"])
def consultar_lote():
    lote = None
    codigo = ""

    if request.method == "POST":
        codigo = request.form.get("codigo", "").strip()
        lote = Lote.query.filter_by(codigo=codigo).first()

        if lote is None:
            flash("No se encontró ningún lote con ese código.", "warning")

    return render_template("consultar_lote.html", lote=lote, codigo=codigo)
