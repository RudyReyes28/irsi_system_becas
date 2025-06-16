from datetime import datetime
from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.utils.authorization import require_role
from app.services.becados_service import (
    convertir_solicitante_a_becado,
    cambiar_estado_becado,
    obtener_becados_activos,
    obtener_timeline_becado,
    obtener_becado_por_id,
    datos_solicitante_convertido
)
from app.models.enums import EstadoBeca

becados_bp = Blueprint('becados', __name__, template_folder='../templates/becados')

@becados_bp.route('/', methods=['GET'])
@login_required
@require_role('Administrador', 'Director', 'Asistente', 'Consulta')
def list_becados():
    cohort = request.args.get('cohort', None)
    becados = obtener_becados_activos(cohort)
    return render_template('becados/list.html', becados=becados)

@becados_bp.route('/convert/<int:solicitante_id>', methods=['POST'])
@login_required
@require_role('Administrador', 'Director')
def convert_solicitante(solicitante_id):
    becado = convertir_solicitante_a_becado(solicitante_id, current_user.id)
    sede = request.form.get('sede', None)
    plataforma = request.form.get('plataforma_externa_id', None)
    conhorte = request.form.get('cohorte', None)
    fecha_inicio = request.form.get('fecha_inicio', None)
    programa = becado.solicitante.programa_solicitado.name if becado.solicitante.programa_solicitado else None
    conhorte = f"{programa}-{conhorte}" if conhorte else None
    datos_solicitante_convertido(becado.id, sede, plataforma, fecha_inicio, conhorte)
    flash('Solicitante convertido a becado exitosamente.', 'success')
    return redirect(url_for('becados.detail_becado', becado_id=becado.id))

@becados_bp.route('/<int:becado_id>', methods=['GET'])
@login_required
@require_role('Administrador', 'Director', 'Asistente', 'Consulta')
def detail_becado(becado_id):
    becado = obtener_becado_por_id(becado_id)
    timeline = obtener_timeline_becado(becado_id)
    return render_template('becados/detail.html', becado=becado, timeline=timeline)

@becados_bp.route('/<int:becado_id>/change_state', methods=['GET','POST'])
@login_required
@require_role('Administrador', 'Director')
def change_state(becado_id):
    if request.method == 'POST':
        nuevo_estado = request.form.get('estado')
        comentario = request.form.get('comentario', '')
        cambiar_estado_becado(becado_id, nuevo_estado, current_user.id, comentario)
        flash(f'Estado cambiado a {nuevo_estado}.', 'success')
        return redirect(url_for('becados.detail_becado', becado_id=becado_id))
    else:
        becado = obtener_becado_por_id(becado_id)
        return render_template('becados/form.html', becado=becado, EstadoBeca=EstadoBeca)
    

@becados_bp.route('/communications/<int:becado_id>', methods=['GET', 'POST'])
def communications(becado_id):
    # Lógica AJAX de comunicaciones internas
    return render_template('becados/communications.html', becado_id=becado_id)

@becados_bp.route('/solicitantes_aprobados', methods=['GET'])
@login_required
@require_role('Administrador', 'Director')
def list_aprobados():
    from app.services.becados_service import obtener_solicitantes_aprobados
    aprobados = obtener_solicitantes_aprobados()
    return render_template('becados/approved.html', aprobados=aprobados)


@becados_bp.route('/todos', methods=['GET'])
@login_required
@require_role('Administrador', 'Director', 'Asistente', 'Consulta')
def list_all_becados():
    """
    Vista para mostrar todos los becados sin importar su estado,
    con filtros avanzados
    """
    # Obtener parámetros de filtro
    search = request.args.get('search', '')
    estado = request.args.get('estado', '')
    cohorte = request.args.get('cohorte', '')
    modalidad = request.args.get('modalidad', '')
    fecha_desde = request.args.get('fecha_desde', '')
    fecha_hasta = request.args.get('fecha_hasta', '')
    
    # Obtener todos los becados con filtros
    from app.services.becados_service import obtener_todos_los_becados_con_filtros
    becados = obtener_todos_los_becados_con_filtros(
        search=search,
        estado=estado,
        cohorte=cohorte,
        modalidad=modalidad,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta
    )

    hoy = date.today()
    for b in becados:
        # suponemos que b.fecha_inicio es un date
        b.dias_transcurridos = (hoy - b.fecha_inicio).days
    
    return render_template('becados/all_becados.html', becados=becados)


# Agregar estas rutas al archivo de rutas de becados

@becados_bp.route('/reportes', methods=['GET'])
@login_required
@require_role('Administrador', 'Director')
def reportes():
    """Dashboard principal de reportes de becados"""
    from app.services.becados_service import (
        obtener_estadisticas_generales_becados,
        obtener_distribucion_por_estado,
        obtener_distribucion_por_cohorte,
        obtener_estadisticas_por_programa,
        obtener_tendencias_mensuales
    )
    
    # Filtros opcionales
    cohorte = request.args.get('cohorte')
    programa = request.args.get('programa')
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    filtros = {
        'cohorte': cohorte,
        'programa': programa,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin
    }
    
    # Obtener datos para los reportes
    estadisticas_generales = obtener_estadisticas_generales_becados(filtros)
    distribucion_estados = obtener_distribucion_por_estado(filtros)
    distribucion_cohortes = obtener_distribucion_por_cohorte(filtros)
    estadisticas_programas = obtener_estadisticas_por_programa(filtros)
    tendencias = obtener_tendencias_mensuales(filtros)
    
    return render_template('becados/reportes.html', 
                         estadisticas_generales=estadisticas_generales,
                         distribucion_estados=distribucion_estados,
                         distribucion_cohortes=distribucion_cohortes,
                         estadisticas_programas=estadisticas_programas,
                         tendencias=tendencias,
                         filtros=filtros)

@becados_bp.route('/reportes/export', methods=['GET'])
@login_required
@require_role('Administrador', 'Director')
def export_reporte():
    """Exportar reportes en formato Excel"""
    from app.services.becados_service import generar_reporte_excel
    import io
    from flask import send_file
    
    # Obtener filtros
    cohorte = request.args.get('cohorte')
    programa = request.args.get('programa')
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    filtros = {
        'cohorte': cohorte,
        'programa': programa,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin
    }
    
    # Generar archivo Excel
    excel_buffer = generar_reporte_excel(filtros)
    
    # Preparar respuesta
    excel_buffer.seek(0)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'reporte_becados_{timestamp}.xlsx'
    
    return send_file(
        io.BytesIO(excel_buffer.read()),
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )

@becados_bp.route('/reportes/detalle/<string:tipo>', methods=['GET'])
@login_required
@require_role('Administrador', 'Director')
def reporte_detalle(tipo):
    """Reportes detallados por tipo específico"""
    from app.services.becados_service import obtener_reporte_detallado
    
    # Validar tipo de reporte
    tipos_validos = ['desercion', 'graduados', 'activos', 'pausados', 'suspendidos']
    if tipo not in tipos_validos:
        flash('Tipo de reporte no válido', 'error')
        return redirect(url_for('becados.reportes'))
    
    # Obtener filtros
    cohorte = request.args.get('cohorte')
    programa = request.args.get('programa')
    
    filtros = {
        'cohorte': cohorte,
        'programa': programa
    }
    
    # Obtener datos del reporte
    datos_reporte = obtener_reporte_detallado(tipo, filtros)
    
    return render_template('becados/reporte_detalle.html', 
                         tipo=tipo,
                         datos=datos_reporte,
                         filtros=filtros)