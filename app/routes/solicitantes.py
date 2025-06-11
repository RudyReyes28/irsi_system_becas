from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models.solicitante import Solicitante
from app.models.historial_estado import HistorialEstado
from app.forms.solicitante_forms import SolicitanteForm
from app.utils.authorization import require_role
from app.models.enums import EstadoSolicitud
from app.services.solicitantes_service import (
    detectar_reaplicacion,
    cambiar_estado_solicitante,
    validar_documentos
)
from werkzeug.utils import secure_filename
import os

solicitantes_bp = Blueprint('solicitantes', __name__, template_folder='../templates/solicitantes')

@solicitantes_bp.route('/', methods=['GET'])
@login_required
@require_role('Administrador', 'Director', 'Asistente', 'Consulta')
def list_solicitantes():
    page = request.args.get('page', 1, type=int)
    filtros = {
        'nombre': request.args.get('nombre', ''),
        'programa': request.args.get('programa', ''),
        'estado': request.args.get('estado', ''),
        'pais': request.args.get('pais', '')
    }

    # Instanciamos el formulario aquí para poder usar sus .choices en la plantilla
    form = SolicitanteForm()

    # Obtenemos la paginación pasando filtros, página y elementos por página
    pagination = Solicitante.buscar_avanzado(filtros, page=page, per_page=10)

    # Enviamos 'form' al render_template
    return render_template(
        'solicitantes/list.html',
        pagination=pagination,
        filtros=filtros,
        form=form
    )

@solicitantes_bp.route('/create', methods=['GET', 'POST'])
@login_required
@require_role('Administrador', 'Director', 'Asistente')
def create_solicitante():
    form = SolicitanteForm()

    if request.method == 'POST':
        # Entramos aquí cada vez que le dan a “Guardar”
        if form.validate_on_submit():
            datos = form.data

            # 1) Detección de reaplicación
            previo = detectar_reaplicacion(datos['emails'], datos['documento'])
            if previo:
                flash('Nota: ya existe una aplicación previa con este email o documento. Se creará una nueva entrada.', 'info')

            # 2) Crear el objeto Solicitante
            solicitante = Solicitante(
                nombre=datos['nombre'],
                emails=datos['emails'],
                documento=datos['documento'],
                fecha_nacimiento=datos['fecha_nacimiento'],
                genero=datos['genero'],
                pais=datos['pais'],
                ciudad=datos['ciudad'],
                telefonos=datos['telefonos'],
                nivel_educativo=datos['nivel_educativo'],
                institucion=datos['institucion'],
                promedio=datos['promedio'],
                experiencia_tech=datos['experiencia_tech'],
                situacion_laboral=datos['situacion_laboral'],
                ingresos=datos['ingresos'],
                acceso_tecnologia=datos['acceso_tecnologia'],
                dependientes=datos['dependientes'],
                programa_solicitado=datos['programa_solicitado'],
                modalidad=datos['modalidad'],
                disponibilidad=datos['disponibilidad'],
                motivacion=datos['motivacion'],
                objetivos=datos['objetivos'],
                estado= EstadoSolicitud.EN_REVISION,
                fecha_registro=datetime.utcnow(),
                fecha_actualizacion=datetime.utcnow()
            )
            db.session.add(solicitante)
            db.session.commit()

            # 3) Crear historial de estado
            cambiar_estado_solicitante(solicitante.id, EstadoSolicitud.EN_REVISION, current_user.id)

            flash('Solicitante creado exitosamente.', 'success')
            return redirect(url_for('solicitantes.list_solicitantes'))

        else:
            # form.validate_on_submit() devolvió False → hay errores
            # Mostramos mensajes debajo de cada campo y recargamos el form
            for campo, errores in form.errors.items():
                for error in errores:
                    flash(f'Error en "{getattr(form, campo).label.text}": {error}', 'danger')

            # NOTA: si quieres que el usuario vea en qué step estaba cuando falló la validación,
            # tendrías que guardar un campo oculto <input name="current_step" …> o similares.
            # De momento, recargamos el form en el paso 1 y mostramos los errores.

    # Si es GET o hubo errores de validación, renderizamos el formulario
    return render_template('solicitantes/form.html', form=form)

@solicitantes_bp.route('/<int:solicitante_id>', methods=['GET'])
@login_required
@require_role('Administrador', 'Director', 'Asistente', 'Consulta')
def detail_solicitante(solicitante_id):
    sol = Solicitante.query.get_or_404(solicitante_id)

    historial = HistorialEstado.query.filter_by(solicitante_id=solicitante_id).order_by(HistorialEstado.fecha.desc()).all()    
    try:
        documentos = sol.listar_documentos()
    except AttributeError:
        documentos = []

    # contar reaplicaciones
    reaplicaciones = Solicitante.query.filter(
        (Solicitante.emails == sol.emails) | 
        (Solicitante.documento == sol.documento)
    ).order_by(Solicitante.fecha_registro.asc()).all()
    mostrar_compare = len(reaplicaciones) > 1
    return render_template(
        'solicitantes/detail.html',
        solicitante=sol,
        historial=historial,
        documentos=documentos,
        EstadoSolicitud=EstadoSolicitud,
        mostrar_compare=mostrar_compare
    )

@solicitantes_bp.route('/<int:solicitante_id>/edit', methods=['GET', 'POST'])
@login_required
@require_role('Administrador', 'Director', 'Asistente')
def edit_solicitante(solicitante_id):
    solicitante = Solicitante.query.get_or_404(solicitante_id)
    form = SolicitanteForm(obj=solicitante)
    if request.method == 'POST' and form.validate():
        datos = form.data
        solicitante.nombre = datos['nombre']
        solicitante.emails=datos['emails']
        solicitante.documento = datos['documento']
        solicitante.fecha_nacimiento = datos['fecha_nacimiento']
        solicitante.genero = datos['genero']
        solicitante.pais = datos['pais']
        solicitante.ciudad = datos['ciudad']
        solicitante.telefonos = datos['telefonos']
        solicitante.nivel_educativo = datos['nivel_educativo']
        solicitante.institucion = datos['institucion']
        solicitante.promedio = datos['promedio']
        solicitante.experiencia_tech = datos['experiencia_tech']
        solicitante.situacion_laboral = datos['situacion_laboral']
        solicitante.ingresos = datos['ingresos']
        solicitante.acceso_tecnologia = datos['acceso_tecnologia']
        solicitante.dependientes = datos['dependientes']
        solicitante.programa_solicitado = datos['programa_solicitado']
        solicitante.modalidad = datos['modalidad']
        solicitante.disponibilidad = datos['disponibilidad']
        solicitante.motivacion = datos['motivacion']
        solicitante.objetivos = datos['objetivos']
        solicitante.fecha_actualizacion = datetime.utcnow()
        db.session.commit()
        flash('Solicitante actualizado correctamente.', 'success')
        return redirect(url_for('solicitantes.detail_solicitante', solicitante_id=solicitante.id))
    return render_template('solicitantes/form.html', form=form, solicitante=solicitante)

@solicitantes_bp.route('/<int:solicitante_id>/change_state', methods=['POST'])
@login_required
@require_role('Administrador', 'Director')
def change_state(solicitante_id):
    nuevo_estado = request.form.get('estado')
    comentario = request.form.get('comentario', '')
    cambiar_estado_solicitante(solicitante_id, nuevo_estado, current_user.id, comentario)
    flash(f'Estado cambiado a {nuevo_estado}.', 'success')
    return redirect(url_for('solicitantes.detail_solicitante', solicitante_id=solicitante_id))

@solicitantes_bp.route('/upload/<int:solicitante_id>', methods=['POST'])
@login_required
@require_role('Administrador', 'Director', 'Asistente')
def upload_document(solicitante_id):
    solicitante = Solicitante.query.get_or_404(solicitante_id)
    file = request.files.get('documento')
    if not file:
        flash('No se seleccionó ningún archivo.', 'danger')
        return redirect(url_for('solicitantes.detail_solicitante', solicitante_id=solicitante_id))
    filename = secure_filename(file.filename)
    if not validar_documentos(filename):
        flash('Formato de archivo no permitido.', 'danger')
        return redirect(url_for('solicitantes.detail_solicitante', solicitante_id=solicitante_id))
    upload_folder = current_app.config.get('UPLOAD_FOLDER_SOLICITANTES')
    camino = os.path.join(upload_folder, str(solicitante_id))
    os.makedirs(camino, exist_ok=True)
    ruta_archivo = os.path.join(camino, filename)
    file.save(ruta_archivo)
    #solicitante.agregar_documento(filename)
    db.session.commit()
    flash('Documento subido exitosamente.', 'success')
    return redirect(url_for('solicitantes.detail_solicitante', solicitante_id=solicitante_id))


@solicitantes_bp.route('/<int:solicitante_id>/compare', methods=['GET', 'POST'])
@login_required
@require_role('Administrador', 'Director', 'Asistente', 'Consulta')
def compare_solicitante(solicitante_id):
    # 1) Recuperamos la aplicación actual
    actual = Solicitante.query.get_or_404(solicitante_id)

    # 2) Buscamos todas las aplicaciones de esta persona (mismo email O mismo documento)
    todas = Solicitante.query.filter(
        (Solicitante.emails == actual.emails) |
        (Solicitante.documento == actual.documento)
    ).order_by(Solicitante.fecha_registro.asc()).all()

    # 3) Inicializamos las dos a comparar
    app1 = actual
    app2 = None

    # 4) Si es POST, tomamos los IDs elegidos en el formulario
    if request.method == 'POST':
        id1 = int(request.form.get('app1'))
        id2 = int(request.form.get('app2'))
        app1 = next((s for s in todas if s.id == id1), actual)
        app2 = next((s for s in todas if s.id == id2), None)

    return render_template(
        'solicitantes/compare.html',
        aplicaciones=todas,
        app1=app1,
        app2=app2
    )
