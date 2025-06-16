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
    obtener_becado_por_id
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