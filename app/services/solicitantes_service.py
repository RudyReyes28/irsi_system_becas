from datetime import datetime
from app import db
from app.models.solicitante import Solicitante
from app.models.historial_estado import HistorialEstado
from app.models.enums import EstadoSolicitud
from sqlalchemy import or_

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}


def detectar_reaplicacion(email: str, documento: str):
    """
    Retorna un solicitante existente si alguno de sus correos (emails)
    contiene el string dado, o si el documento coincide exactamente.
    """
    return Solicitante.query.filter(
        or_(
            Solicitante.emails.ilike(f"%{email}%"),
            Solicitante.documento == documento
        )
    ).first()

def cambiar_estado_solicitante(solicitante_id: int, nuevo_estado: EstadoSolicitud, usuario_id: int, comentario: str = ''):
    """
    Crea un registro en HistorialEstado y actualiza el estado.
    'nuevo_estado' debe ser un miembro de EstadoSolicitud, no un string arbitrario.
    """
    solicitante = Solicitante.query.get_or_404(solicitante_id)

    # Registramos en historial
    historial = HistorialEstado(
        solicitante_id=solicitante_id,
        usuario_id=usuario_id,   # <-- quién hizo el cambio
        estado=nuevo_estado,
        fecha=datetime.utcnow(),
        comentario=comentario         # <-- debe coincidir con el nombre de la columna
    )

    # Actualizamos el estado en el modelo
    solicitante.estado = nuevo_estado
    solicitante.fecha_actualizacion = datetime.utcnow()

    db.session.add(historial)
    db.session.commit()


def validar_documentos(filename: str) -> bool:
    ext = filename.rsplit('.', 1)[-1].lower()
    return ext in ALLOWED_EXTENSIONS