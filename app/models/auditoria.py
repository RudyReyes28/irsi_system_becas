# app/utils/auditoria.py
from flask import request
from app.models import AuditoriaActividad
from app import db
import json

def auditar_cambio(usuario_id, tabla, operacion, id_registro, datos_antes, datos_despues):
    auditoria = AuditoriaActividad(
        usuario_id=usuario_id,
        tabla_afectada=tabla,
        operacion=operacion,
        id_registro=id_registro,
        datos_antes=json.dumps(datos_antes, default=str),
        datos_despues=json.dumps(datos_despues, default=str),
        ip=request.remote_addr
    )
    db.session.add(auditoria)

__table_args__ = (
    db.Index('idx_becado_estado', 'estado'),
    db.Index('idx_auditoria_usuario_fecha', 'usuario_id', 'timestamp'),
)