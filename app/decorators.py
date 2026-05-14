from functools import wraps
from flask import abort
from flask_login import current_user


def roles_requeridos(*roles_permitidos):
    """Permite acceder a una ruta solo si el usuario tiene uno de los roles indicados."""

    def decorador(funcion):
        @wraps(funcion)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)

            if current_user.role is None or current_user.role.name not in roles_permitidos:
                abort(403)

            return funcion(*args, **kwargs)

        return wrapper

    return decorador
