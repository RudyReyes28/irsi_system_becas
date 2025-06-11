from datetime import datetime
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

@becados_bp.route('/<int:becado_id>/change_state', methods=['POST'])
@login_required
@require_role('Administrador', 'Director')
def change_state(becado_id):
    nuevo_estado = request.form.get('estado')
    comentario = request.form.get('comentario', '')
    cambiar_estado_becado(becado_id, nuevo_estado, current_user.id, comentario)
    flash(f'Estado cambiado a {nuevo_estado}.', 'success')
    return redirect(url_for('becados.detail_becado', becado_id=becado_id))

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
