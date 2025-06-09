# app/models/__init__.py
from .user import User
from .auditoria_login import AuditoriaLogin
from .solicitante import Solicitante
from .historial_estado import HistorialEstado
from .enums import EstadoSolicitud, Genero, Pais, Programa, Modalidad, EstadoBeca
from .becado import Becado
from .estado_becado import EstadoBecado
from .auditoria_actividad import AuditoriaActividad
from .auditoria import auditar_cambio

all_models = [
    User,
    AuditoriaLogin,
    Solicitante,
    HistorialEstado,
    EstadoSolicitud,
    Genero,
    Pais,
    Programa,
    Modalidad,
    EstadoBeca,
    Becado,
    EstadoBecado,
    AuditoriaActividad
]

__all__ = [
    'User',
    'AuditoriaLogin',
    'Solicitante',
    'HistorialEstado',
    'EstadoSolicitud',
    'Genero',
    'Pais',
    'Programa',
    'Modalidad',
    'EstadoBeca',
    'Becado',
    'EstadoBecado',
    'AuditoriaActividad',
    'auditar_cambio',
    'all_models'
]