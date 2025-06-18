# app/routes/main.py
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from app import db
from app.models.solicitante import Solicitante
from app.models.becado import Becado
from app.models.historial_estado import HistorialEstado  # Asumiendo que tienes este modelo
from app.models.enums import EstadoSolicitud, EstadoBeca

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def index():
    rol = current_user.rol
    
    # Obtener estadísticas generales
    estadisticas = obtener_estadisticas_dashboard()
    
    # Obtener actividad reciente
    actividad_reciente = obtener_actividad_reciente()
    
    # Obtener información de fechas importantes (puedes personalizarlo)
    fechas_importantes = obtener_fechas_importantes()
    
    # Obtener progreso general
    progreso = calcular_progreso_general()
    
    return render_template(
        'index.html', 
        rol=rol,
        estadisticas=estadisticas,
        actividad_reciente=actividad_reciente,
        fechas_importantes=fechas_importantes,
        progreso=progreso
    )

def obtener_estadisticas_dashboard():
    """Obtiene las estadísticas principales del dashboard"""
    try:
        # Total de solicitantes
        total_solicitantes = Solicitante.query.count()
        
        # Becas aprobadas (solicitantes con estado aprobado)
        becas_aprobadas = Solicitante.query.filter_by(estado=EstadoSolicitud.APROBADO).count()
        
        # En revisión
        en_revision = Solicitante.query.filter_by(estado=EstadoSolicitud.EN_REVISION).count()
        
        # Becados activos (si tienes el modelo Becado)
        try:
            becados_activos = Becado.query.filter_by(estado=EstadoBeca.ACTIVO).count()
        except:
            # Si no tienes el modelo Becado o EstadoBeca, usa una alternativa
            becados_activos = Solicitante.query.filter_by(estado=EstadoSolicitud.APROBADO).count()
        
        return {
            'total_solicitantes': total_solicitantes,
            'becas_aprobadas': becas_aprobadas,
            'en_revision': en_revision,
            'becados_activos': becados_activos
        }
    except Exception as e:
        # En caso de error, devolver valores por defecto
        return {
            'total_solicitantes': 0,
            'becas_aprobadas': 0,
            'en_revision': 0,
            'becados_activos': 0
        }

def obtener_actividad_reciente():
    """Obtiene la actividad reciente del sistema"""
    actividades = []
    
    try:
        # Obtener los últimos 5 solicitantes registrados
        solicitantes_recientes = (Solicitante.query
                                .order_by(desc(Solicitante.fecha_registro))
                                .limit(3)
                                .all())
        
        for solicitante in solicitantes_recientes:
            tiempo_transcurrido = calcular_tiempo_transcurrido(solicitante.fecha_registro)
            
            if solicitante.estado == EstadoSolicitud.APROBADO:
                actividades.append({
                    'tipo': 'aprobacion',
                    'icono': 'bi-check-circle',
                    'color': 'success',
                    'titulo': 'Solicitud Aprobada',
                    'descripcion': f"{solicitante.nombre} - {solicitante.programa_legible}",
                    'tiempo': tiempo_transcurrido
                })
            elif solicitante.estado == EstadoSolicitud.EN_REVISION:
                actividades.append({
                    'tipo': 'nueva_solicitud',
                    'icono': 'bi-person-plus',
                    'color': 'primary',
                    'titulo': 'Nueva Solicitud',
                    'descripcion': f"{solicitante.nombre} - {solicitante.programa_legible}",
                    'tiempo': tiempo_transcurrido
                })
            elif solicitante.estado == EstadoSolicitud.REGISTRADO:
                actividades.append({
                    'tipo': 'documentacion_pendiente',
                    'icono': 'bi-exclamation-triangle',
                    'color': 'warning',
                    'titulo': 'Documentación Pendiente',
                    'descripcion': f"{solicitante.nombre} - Requiere documentos",
                    'tiempo': tiempo_transcurrido
                })
        
        # Si no hay suficientes actividades reales, puedes agregar algunas por defecto
        if len(actividades) < 3:
            actividades.extend(get_actividades_por_defecto())
            
        return actividades[:3]  # Limitar a 3 actividades
        
    except Exception as e:
        return get_actividades_por_defecto()

def get_actividades_por_defecto():
    """Actividades por defecto cuando no hay datos suficientes"""
    return [
        {
            'tipo': 'sistema',
            'icono': 'bi-gear',
            'color': 'info',
            'titulo': 'Sistema Iniciado',
            'descripcion': 'Sistema de gestión de becas operativo',
            'tiempo': 'Reciente'
        }
    ]

def calcular_tiempo_transcurrido(fecha):
    """Calcula el tiempo transcurrido desde una fecha"""
    try:
        ahora = datetime.utcnow()
        diferencia = ahora - fecha
        
        if diferencia.days > 0:
            return f"Hace {diferencia.days} día{'s' if diferencia.days > 1 else ''}"
        elif diferencia.seconds > 3600:
            horas = diferencia.seconds // 3600
            return f"Hace {horas} hora{'s' if horas > 1 else ''}"
        elif diferencia.seconds > 60:
            minutos = diferencia.seconds // 60
            return f"Hace {minutos} minuto{'s' if minutos > 1 else ''}"
        else:
            return "Hace unos momentos"
    except:
        return "Reciente"

def obtener_fechas_importantes():
    """Obtiene fechas importantes del sistema"""
    # Estas fechas pueden venir de una tabla de configuración o ser calculadas
    return {
        'cierre_convocatoria': '15 de Julio, 2025',
        'resultados': '30 de Julio, 2025'
    }

def calcular_progreso_general():
    """Calcula el progreso general del sistema"""
    try:
        total_solicitantes = Solicitante.query.count()
        if total_solicitantes == 0:
            return {'porcentaje': 0, 'procesadas': 0, 'total': 0}
        
        # Consideramos como "procesadas" las que no están en estado REGISTRADO
        procesadas = Solicitante.query.filter(
            Solicitante.estado != EstadoSolicitud.REGISTRADO
        ).count()
        
        porcentaje = int((procesadas / total_solicitantes) * 100) if total_solicitantes > 0 else 0
        
        return {
            'porcentaje': porcentaje,
            'procesadas': procesadas,
            'total': total_solicitantes
        }
    except:
        return {'porcentaje': 0, 'procesadas': 0, 'total': 0}

# Funciones adicionales para estadísticas más específicas por rol
def obtener_estadisticas_por_rol(rol):
    """Obtiene estadísticas específicas según el rol del usuario"""
    estadisticas_base = obtener_estadisticas_dashboard()
    
    if rol == 'Administrador':
        # Estadísticas completas para administrador
        estadisticas_base.update({
            'usuarios_activos': get_usuarios_activos(),
            'solicitudes_mes': get_solicitudes_mes_actual()
        })
    elif rol == 'Director':
        # Estadísticas ejecutivas para director
        estadisticas_base.update({
            'tasa_aprobacion': calcular_tasa_aprobacion(),
            'programas_populares': get_programas_mas_solicitados()
        })
    
    return estadisticas_base

def get_usuarios_activos():
    """Obtiene el número de usuarios activos (si tienes el modelo User)"""
    try:
        from app.models.user import User
        return User.query.filter_by(activo=True).count()
    except:
        return 0

def get_solicitudes_mes_actual():
    """Obtiene las solicitudes del mes actual"""
    try:
        inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return Solicitante.query.filter(Solicitante.fecha_registro >= inicio_mes).count()
    except:
        return 0

def calcular_tasa_aprobacion():
    """Calcula la tasa de aprobación de solicitudes"""
    try:
        total = Solicitante.query.count()
        aprobados = Solicitante.query.filter_by(estado=EstadoSolicitud.APROBADO).count()
        return round((aprobados / total) * 100, 1) if total > 0 else 0
    except:
        return 0

def get_programas_mas_solicitados():
    """Obtiene los programas más solicitados"""
    try:
        programas = (db.session.query(Solicitante.programa_solicitado, func.count(Solicitante.id))
                    .group_by(Solicitante.programa_solicitado)
                    .order_by(desc(func.count(Solicitante.id)))
                    .limit(3)
                    .all())
        return [{'programa': p[0].name, 'cantidad': p[1]} for p in programas]
    except:
        return []
    
