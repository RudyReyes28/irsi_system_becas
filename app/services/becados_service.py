# app/services/becados_service.py

from datetime import datetime
from app import db
from app.models.solicitante import Solicitante
from app.models.becado import Becado
from app.models.estado_becado import EstadoBecado
from app.models.enums import EstadoSolicitud, EstadoBeca
from app.models.historial_estado import HistorialEstado
from sqlalchemy import func, extract, and_, or_
from datetime import datetime, date
import io
import pandas as pd


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

def datos_solicitante_convertido(becado_id:int, sede:str, plataforma_externa_id:str, fecha_inicio:str, cohorte:str):
    """
    Actualiza los datos del becado convertido.
    """
    becado = obtener_becado_por_id(becado_id)
    
    # Actualizar los campos del becado
    if sede:
        becado.sede = sede
    if plataforma_externa_id:
        becado.plataforma_externa_id = plataforma_externa_id
    if cohorte:
        becado.cohorte = cohorte
    if fecha_inicio:
        from datetime import datetime
        fecha_inicio_obj = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        becado.fecha_inicio = fecha_inicio_obj
    
    db.session.commit()
    return becado


def obtener_estadisticas_generales_becados(filtros=None):
    """Obtiene estadísticas generales de becados"""
    query = db.session.query(Becado).join(Solicitante)
    
    # Aplicar filtros
    if filtros:
        query = aplicar_filtros_becados(query, filtros)
    
    total_becados = query.count()
    
    # Contar por estado
    estadisticas_estados = db.session.query(
        Becado.estado,
        func.count(Becado.id).label('cantidad')
    ).join(Solicitante)
    
    if filtros:
        estadisticas_estados = aplicar_filtros_becados(estadisticas_estados, filtros)
    
    estadisticas_estados = estadisticas_estados.group_by(Becado.estado).all()
    
    # Calcular porcentajes
    estados_dict = {}
    for estado, cantidad in estadisticas_estados:
        porcentaje = (cantidad / total_becados * 100) if total_becados > 0 else 0
        estados_dict[estado.value] = {
            'cantidad': cantidad,
            'porcentaje': round(porcentaje, 2)
        }
    
    return {
        'total_becados': total_becados,
        'estados': estados_dict,
        'activos': estados_dict.get('Activo', {}).get('cantidad', 0),
        'graduados': estados_dict.get('Graduado', {}).get('cantidad', 0),
        'desertores': estados_dict.get('Desertor', {}).get('cantidad', 0)
    }

def obtener_distribucion_por_estado(filtros=None):
    """Obtiene la distribución de becados por estado"""
    query = db.session.query(
        Becado.estado,
        func.count(Becado.id).label('cantidad')
    ).join(Solicitante)
    
    if filtros:
        query = aplicar_filtros_becados(query, filtros)
    
    resultados = query.group_by(Becado.estado).all()
    
    return [
        {
            'estado': estado.value,
            'cantidad': cantidad
        }
        for estado, cantidad in resultados
    ]

def obtener_distribucion_por_cohorte(filtros=None):
    """Obtiene la distribución de becados por cohorte"""
    query = db.session.query(
        Becado.cohorte,
        Becado.estado,
        func.count(Becado.id).label('cantidad')
    ).join(Solicitante)
    
    if filtros:
        query = aplicar_filtros_becados(query, filtros)
    
    resultados = query.group_by(Becado.cohorte, Becado.estado).all()
    
    # Organizar datos por cohorte
    cohortes_dict = {}
    for cohorte, estado, cantidad in resultados:
        if cohorte not in cohortes_dict:
            cohortes_dict[cohorte] = {}
        cohortes_dict[cohorte][estado.value] = cantidad
    
    return cohortes_dict

def obtener_estadisticas_por_programa(filtros=None):
    """Obtiene estadísticas por programa académico"""
    query = db.session.query(
        Solicitante.programa_solicitado,
        Becado.estado,
        func.count(Becado.id).label('cantidad')
    ).join(Becado, Solicitante.id == Becado.solicitante_id)
    
    if filtros:
        query = aplicar_filtros_becados(query, filtros)
    
    resultados = query.group_by(Solicitante.programa_solicitado, Becado.estado).all()
    
    # Organizar datos por programa
    programas_dict = {}
    for programa, estado, cantidad in resultados:
        if programa.value not in programas_dict:
            programas_dict[programa.value] = {}
        programas_dict[programa.value][estado.value] = cantidad
    
    return programas_dict

def obtener_tendencias_mensuales(filtros=None):
    """Obtiene tendencias mensuales de estados de becados"""
    query = db.session.query(
        extract('year', EstadoBecado.fecha).label('año'),
        extract('month', EstadoBecado.fecha).label('mes'),
        EstadoBecado.estado,
        func.count(EstadoBecado.id).label('cantidad')
    ).join(Becado, EstadoBecado.becado_id == Becado.id)\
     .join(Solicitante, Becado.solicitante_id == Solicitante.id)
    
    if filtros:
        query = aplicar_filtros_estados_historial(query, filtros)
    
    # Filtrar últimos 12 meses
    fecha_limite = datetime.now().replace(day=1) - pd.DateOffset(months=11)
    query = query.filter(EstadoBecado.fecha >= fecha_limite)
    
    resultados = query.group_by(
        extract('year', EstadoBecado.fecha),
        extract('month', EstadoBecado.fecha),
        EstadoBecado.estado
    ).order_by('año', 'mes').all()
    
    # Organizar datos por mes
    tendencias = {}
    for año, mes, estado, cantidad in resultados:
        fecha_key = f"{int(año)}-{int(mes):02d}"
        if fecha_key not in tendencias:
            tendencias[fecha_key] = {}
        tendencias[fecha_key][estado.value] = cantidad
    
    return tendencias

def obtener_reporte_detallado(tipo, filtros=None):
    """Obtiene reporte detallado por tipo específico"""
    # Mapear tipo a estado
    estado_map = {
        'desercion': EstadoBeca.DESERTOR,
        'graduados': EstadoBeca.GRADUADO,
        'activos': EstadoBeca.ACTIVO,
        'pausados': EstadoBeca.EN_PAUSA,
        'suspendidos': EstadoBeca.SUSPENDIDO
    }
    
    estado_filtro = estado_map.get(tipo)
    if not estado_filtro:
        return []
    
    query = db.session.query(
        Becado,
        Solicitante
    ).join(Solicitante, Becado.solicitante_id == Solicitante.id)\
     .filter(Becado.estado == estado_filtro)
    
    if filtros:
        query = aplicar_filtros_becados(query, filtros)
    
    resultados = query.all()
    
    datos = []
    for becado, solicitante in resultados:
        # Obtener último cambio de estado
        ultimo_cambio = db.session.query(EstadoBecado)\
            .filter_by(becado_id=becado.id, estado=estado_filtro)\
            .order_by(EstadoBecado.fecha.desc())\
            .first()
        
        datos.append({
            'id': becado.id,
            'nombre': solicitante.nombre,
            'documento': solicitante.documento,
            'programa': solicitante.programa_solicitado.value,
            'cohorte': becado.cohorte,
            'modalidad': becado.modalidad.value,
            'fecha_inicio': becado.fecha_inicio,
            'fecha_cambio_estado': ultimo_cambio.fecha if ultimo_cambio else None,
            'observacion': ultimo_cambio.observacion if ultimo_cambio else None
        })
    
    return datos

def generar_reporte_excel(filtros=None):
    """Genera reporte completo en formato Excel"""
    # Crear buffer en memoria
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Hoja 1: Estadísticas generales
        stats = obtener_estadisticas_generales_becados(filtros)
        df_stats = pd.DataFrame([
            ['Total Becados', stats['total_becados']],
            ['Activos', stats['activos']],
            ['Graduados', stats['graduados']],
            ['Desertores', stats['desertores']]
        ], columns=['Métrica', 'Valor'])
        df_stats.to_excel(writer, sheet_name='Estadísticas Generales', index=False)
        
        # Hoja 2: Distribución por estado
        distribucion_estados = obtener_distribucion_por_estado(filtros)
        df_estados = pd.DataFrame(distribucion_estados)
        df_estados.to_excel(writer, sheet_name='Por Estado', index=False)
        
        # Hoja 3: Distribución por cohorte
        distribucion_cohortes = obtener_distribucion_por_cohorte(filtros)
        cohortes_data = []
        for cohorte, estados in distribucion_cohortes.items():
            for estado, cantidad in estados.items():
                cohortes_data.append({
                    'cohorte': cohorte,
                    'estado': estado,
                    'cantidad': cantidad
                })
        df_cohortes = pd.DataFrame(cohortes_data)
        df_cohortes.to_excel(writer, sheet_name='Por Cohorte', index=False)
        
        # Hoja 4: Reporte detallado de activos
        activos_detalle = obtener_reporte_detallado('activos', filtros)
        df_activos = pd.DataFrame(activos_detalle)
        if not df_activos.empty:
            df_activos.to_excel(writer, sheet_name='Becados Activos', index=False)
        
        # Hoja 5: Reporte detallado de graduados
        graduados_detalle = obtener_reporte_detallado('graduados', filtros)
        df_graduados = pd.DataFrame(graduados_detalle)
        if not df_graduados.empty:
            df_graduados.to_excel(writer, sheet_name='Graduados', index=False)
    
    return output

def aplicar_filtros_becados(query, filtros):
    """Aplica filtros a la consulta de becados"""
    if filtros.get('cohorte'):
        query = query.filter(Becado.cohorte == filtros['cohorte'])
    
    if filtros.get('programa'):
        query = query.filter(Solicitante.programa_solicitado == filtros['programa'])
    
    if filtros.get('fecha_inicio'):
        fecha_inicio = datetime.strptime(filtros['fecha_inicio'], '%Y-%m-%d').date()
        query = query.filter(Becado.fecha_inicio >= fecha_inicio)
    
    if filtros.get('fecha_fin'):
        fecha_fin = datetime.strptime(filtros['fecha_fin'], '%Y-%m-%d').date()
        query = query.filter(Becado.fecha_inicio <= fecha_fin)
    
    return query

def aplicar_filtros_estados_historial(query, filtros):
    """Aplica filtros a la consulta del historial de estados"""
    if filtros.get('cohorte'):
        query = query.filter(Becado.cohorte == filtros['cohorte'])
    
    if filtros.get('programa'):
        query = query.filter(Solicitante.programa_solicitado == filtros['programa'])
    
    return query