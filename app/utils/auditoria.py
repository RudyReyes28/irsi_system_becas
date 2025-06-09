# app/utils/auditoria.py

import json
from flask import request
from app import db
from app.models.auditoria_actividad import AuditoriaActividad

def auditar_cambio(usuario_id: int, tabla: str, operacion: str, id_registro: int, datos_antes: dict, datos_despues: dict):
    """
    Registra un log de auditoría.
    
    Args:
        usuario_id: ID del usuario que realizó la acción.
        tabla: Nombre de la tabla afectada (por ejemplo, 'usuarios').
        operacion: Tipo de operación: 'CREATE', 'UPDATE' o 'DELETE'.
        id_registro: ID del registro afectado en la tabla.
        datos_antes: Diccionario con los valores anteriores (o {} si CREATE).
        datos_despues: Diccionario con los valores nuevos (o {} si DELETE).
    """
    try:
        log = AuditoriaActividad(
            usuario_id=usuario_id,
            tabla_afectada=tabla,
            operacion=operacion,
            id_registro=id_registro,
            datos_antes=json.dumps(datos_antes, default=str),
            datos_despues=json.dumps(datos_despues, default=str),
            ip=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        # En caso de error en auditoría, opcionalmente hacer rollback o registrar en log de archivos
        db.session.rollback()
        # Aquí podrías usar `current_app.logger.error(...)` si importas current_app
        print(f"Error al registrar auditoría: {e}")
