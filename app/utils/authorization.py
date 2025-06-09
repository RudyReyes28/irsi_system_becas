# app/utils/authorization.py

from functools import wraps
from flask import abort
from flask_login import current_user

# Definimos los roles disponibles
ROLES = {
    'Administrador',
    'Director',
    'Asistente',
    'Consulta'
}

# Matriz de permisos (funcionalidades a etiquetas de permiso):
# Ajusta estas claves según el nombre interno que uses en tu app
PERMISSIONS = {
    'gestion_usuarios': {'Administrador'},
    'aprobacion_becas': {'Administrador', 'Director'},
    'registro_solicitantes': {'Administrador', 'Director', 'Asistente'},
    'ver_reportes_operativos': {'Administrador', 'Director', 'Asistente', 'Consulta'},
    'ver_reportes_ejecutivos': {'Administrador', 'Director'},
    'importacion_masiva': {'Administrador', 'Asistente'},
    'auditoria': {'Administrador', 'Director'},
    # Agrega más funcionalidades según tu matriz
}


def require_role(*allowed_roles):
    """
    Decorador que solo deja pasar si current_user.rol está en allowed_roles.
    Ejemplo: @require_role('Administrador', 'Director')
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return abort(401)
            if current_user.rol not in allowed_roles:
                return abort(403)
            return f(*args, **kwargs)
        return wrapped
    return decorator


def has_permission(permission_key: str) -> bool:
    """
    Verifica si current_user.rol tiene permiso para la funcionalidad dada.
    - permission_key debe existir en PERMISSIONS; de lo contrario, retorna False.
    """
    if not current_user.is_authenticated:
        return False
    roles_permitidos = PERMISSIONS.get(permission_key, set())
    return current_user.rol in roles_permitidos
