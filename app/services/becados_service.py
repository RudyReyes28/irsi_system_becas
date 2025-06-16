# app/services/becados_service.py

from datetime import datetime
from app import db
from app.models.solicitante import Solicitante
from app.models.becado import Becado
from app.models.estado_becado import EstadoBecado
from app.models.enums import EstadoSolicitud, EstadoBeca
from app.models.historial_estado import HistorialEstado


def convertir_solicitante_a_becado(solicitante_id: int, usuario_id: int) -> Becado:
    """
    Convierte un solicitante aprobado en un becado.
    Registra también la entrada inicial en el historial de estados.
    """
    solicitante = Solicitante.query.get_or_404(solicitante_id)
    if solicitante.estado != EstadoSolicitud.APROBADO:
        raise ValueError("Solo se pueden convertir solicitantes aprobados.")

    # Crear el registro de Becado
    becado = Becado(
        solicitante_id=solicitante.id,
        cohorte=f"{solicitante.programa_solicitado.name}-{datetime.utcnow().year}",
        fecha_inicio=datetime.utcnow().date(),
        modalidad=solicitante.modalidad,
        sede=None,
        plataforma_externa_id=None
    )
    db.session.add(becado)
    db.session.flush()  # Para obtener becado.id antes de commit

    # Registrar la entrada inicial en el historial de estados del becado
    estado0 = EstadoBecado(
        becado_id=becado.id,
        usuario_id=usuario_id,
        estado=EstadoBeca.ACTIVO,
        fecha=datetime.utcnow(),
        observacion="Creación de becado"
    )
    db.session.add(estado0)

    # Cambiar el estado del solicitante a CONVERTIDO
    solicitante.estado = EstadoSolicitud.CONVERTIDO
    #cambiar el historial del solicitante
    historial = HistorialEstado(
        solicitante_id=solicitante_id,
        usuario_id=usuario_id,   # <-- quién hizo el cambio
        estado=EstadoSolicitud.CONVERTIDO,
        fecha=datetime.utcnow(),
        comentario='Se ha becado a este solicitante'         # <-- debe coincidir con el nombre de la columna
    )
    db.session.add(historial)

    db.session.commit()
    return becado


def obtener_becados_activos(cohort: str = None):
    """
    Devuelve todos los becados cuyo estado sea ACTIVO.
    Si se suministra 'cohort', filtra por esa cohorte.
    """
    query = Becado.query.filter(Becado.estado == EstadoBeca.ACTIVO)
    if cohort:
        query = query.filter(Becado.cohorte == cohort)
    return query.order_by(Becado.fecha_inicio.desc()).all()


def obtener_becado_por_id(becado_id: int) -> Becado:
    """
    Recupera un becado por su ID o lanza 404 si no existe.
    """
    return Becado.query.get_or_404(becado_id)


def cambiar_estado_becado(becado_id: int, nuevo_estado: EstadoBeca, usuario_id: int, comentario: str = ''):
    """
    Cambia el estado de un becado y registra la transición en EstadoBecado.
    """
    becado = obtener_becado_por_id(becado_id)

    # Registrar nueva entrada en el historial
    entry = EstadoBecado(
        becado_id=becado.id,
        usuario_id=usuario_id,
        estado=nuevo_estado,
        fecha=datetime.utcnow(),
        observacion=comentario
    )
    db.session.add(entry)

    # Actualizar el estado actual del becado
    becado.estado = nuevo_estado
    becado.fecha_ultimo_cambio_estado = datetime.utcnow()

    db.session.commit()


def obtener_timeline_becado(becado_id: int):
    """
    Recupera todas las entradas de EstadoBecado de un becado
    ordenadas cronológicamente.
    """
    return (
        EstadoBecado.query
        .filter_by(becado_id=becado_id)
        .order_by(EstadoBecado.fecha.asc())
        .all()
    )


def obtener_solicitantes_aprobados():
    """
    Retorna todos los solicitantes cuyo estado sea APROBADO,
    para poder convertirlos en becados.
    """
    return Solicitante.query.filter(
        Solicitante.estado == EstadoSolicitud.APROBADO
    ).order_by(Solicitante.fecha_registro.desc()).all()

# Agregar esta función a tu becados_service.py

def obtener_todos_los_becados_con_filtros(search=None, estado=None, cohorte=None, 
                                         modalidad=None, fecha_desde=None, fecha_hasta=None):
    """
    Obtiene todos los becados con filtros opcionales
    """
    from app.models.becado import Becado
    from app.models.solicitante import Solicitante
    from datetime import datetime
    
    # Query base
    query = db.session.query(Becado).join(Solicitante)
    
    # Aplicar filtros
    if search:
        query = query.filter(
            db.or_(
                Solicitante.nombre.ilike(f'%{search}%'),
                Solicitante.documento.ilike(f'%{search}%'),
                Becado.id.like(f'%{search}%')
            )
        )
    
    if estado:
        from app.models.enums import EstadoBeca
        query = query.filter(Becado.estado == EstadoBeca[estado])
    
    if cohorte:
        query = query.filter(Becado.cohorte == cohorte)
    
    if modalidad:
        from app.models.enums import Modalidad
        query = query.filter(Becado.modalidad == Modalidad[modalidad])
    
    if fecha_desde:
        fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
        query = query.filter(Becado.fecha_inicio >= fecha_desde_obj)
    
    if fecha_hasta:
        fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
        query = query.filter(Becado.fecha_inicio <= fecha_hasta_obj)
    
    # Ordenar por fecha de inicio descendente
    return query.order_by(Becado.fecha_inicio.desc()).all()