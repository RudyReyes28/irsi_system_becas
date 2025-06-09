# app/utils/decorators.py

from functools import wraps
from flask import abort
from flask_login import current_user

def roles_required(*roles):
    """
    Decorador que exige que current_user.rol esté en los roles dados.
    Ejemplo: @roles_required('Administrador', 'Director')
    """
    def wrapper(f):
        @wraps(f)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return abort(401)
            if current_user.rol not in roles:
                return abort(403)
            return f(*args, **kwargs)
        return decorated_view
    return wrapper
