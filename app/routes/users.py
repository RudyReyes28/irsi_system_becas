from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.forms.user_forms import UserForm, PasswordResetForm
from app.utils.authorization import require_role
from app.utils.auditoria import auditar_cambio

users_bp = Blueprint('users', __name__, template_folder='../templates/users')

@users_bp.route('/', methods=['GET'])
@login_required
@require_role('Administrador')
def list_users():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    query = User.query
    if search:
        query = query.filter(User.email.ilike(f"%{search}%"))
    pagination = query.order_by(User.fecha_creacion.desc()).paginate(page=page, per_page=10)
    return render_template('users/list.html', pagination=pagination, search=search)

@users_bp.route('/create', methods=['GET', 'POST'])
@login_required
@require_role('Administrador')
def create_user():
    form = UserForm()
    if form.validate_on_submit():
        existing = User.query.filter_by(email=form.email.data).first()
        if existing:
            flash('El correo ya está en uso.', 'danger')
            return render_template('form.html', form=form)
        user = User(
            nombre=form.nombre.data,
            email=form.email.data,
            rol=form.rol.data,
            activo=True,
            fecha_creacion=datetime.utcnow()
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        auditar_cambio(current_user.id, 'usuarios', 'CREATE', user.id, {}, {
            'nombre': user.nombre,
            'email': user.email,
            'rol': user.rol,
            'activo': user.activo
        })
        flash('Usuario creado correctamente.', 'success')
        return redirect(url_for('users.list_users'))
    return render_template('users/form.html', form=form)

@users_bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@require_role('Administrador')
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    form.password.validators = []  # no obligatorio al editar
    if request.method == 'POST' and form.validate():
        datos_antes = {'nombre': user.nombre, 'email': user.email, 'rol': user.rol, 'activo': user.activo}
        user.nombre = form.nombre.data
        if user.email != form.email.data:
            if User.query.filter_by(email=form.email.data).first():
                flash('El correo ya está en uso.', 'danger')
                return render_template('users/form.html', form=form, user=user)
            user.email = form.email.data
        user.rol = form.rol.data
        if form.password.data:
            user.set_password(form.password.data)
        db.session.commit()
        datos_despues = {'nombre': user.nombre, 'email': user.email, 'rol': user.rol, 'activo': user.activo}
        auditar_cambio(current_user.id, 'usuarios', 'UPDATE', user.id, datos_antes, datos_despues)
        flash('Usuario actualizado correctamente.', 'success')
        return redirect(url_for('users.list_users'))
    return render_template('users/form.html', form=form, user=user)

@users_bp.route('/<int:user_id>/toggle_active', methods=['POST'])
@login_required
@require_role('Administrador')
def toggle_active(user_id):
    user = User.query.get_or_404(user_id)
    datos_antes = {'activo': user.activo}
    user.activo = not user.activo
    db.session.commit()
    datos_despues = {'activo': user.activo}
    auditar_cambio(current_user.id, 'usuarios', 'UPDATE', user.id, datos_antes, datos_despues)
    return jsonify({'success': True, 'activo': user.activo})

@users_bp.route('/<int:user_id>/delete', methods=['POST'])
@login_required
@require_role('Administrador')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    datos_antes = {'nombre': user.nombre, 'email': user.email, 'rol': user.rol, 'activo': user.activo}
    db.session.delete(user)
    db.session.commit()
    auditar_cambio(current_user.id, 'usuarios', 'DELETE', user_id, datos_antes, {})
    flash('Usuario eliminado correctamente.', 'success')
    return redirect(url_for('users.list_users'))

@users_bp.route('/<int:user_id>', methods=['GET'])
@login_required
@require_role('Administrador')
def detail_user(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('users/detail.html', user=user)

@users_bp.route('/<int:user_id>/reset_password', methods=['GET', 'POST'])
@login_required
@require_role('Administrador')
def reset_password(user_id):
    user = User.query.get_or_404(user_id)
    form = PasswordResetForm()
    if form.validate_on_submit():
        datos_antes = {'password_hash': user.password_hash}
        user.set_password(form.password.data)
        user.reset_failed_attempts()
        db.session.commit()
        datos_despues = {'password_hash': user.password_hash}
        auditar_cambio(current_user.id, 'usuarios', 'UPDATE', user.id, datos_antes, datos_despues)
        flash('Contraseña restablecida correctamente.', 'success')
        return redirect(url_for('users.detail_user', user_id=user.id))
    return render_template('reset_password.html', form=form, user=user)

# Agregar esta ruta a tu archivo de rutas users.py

@users_bp.route('/<int:user_id>/reset_failed_attempts', methods=['POST'])
@login_required
@require_role('Administrador')
def reset_failed_attempts(user_id):
    """Restablece los intentos fallidos de login de un usuario"""
    user = User.query.get_or_404(user_id)
    datos_antes = {
        'intentos_fallidos': user.intentos_fallidos,
        'ultimo_intento_fallido': user.ultimo_intento_fallido
    }
    
    user.reset_failed_attempts()
    db.session.commit()
    
    datos_despues = {
        'intentos_fallidos': user.intentos_fallidos,
        'ultimo_intento_fallido': user.ultimo_intento_fallido
    }
    
    auditar_cambio(current_user.id, 'usuarios', 'UPDATE', user.id, datos_antes, datos_despues)
    
    return jsonify({
        'success': True, 
        'message': 'Intentos fallidos restablecidos correctamente'
    })