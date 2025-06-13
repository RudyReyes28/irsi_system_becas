# app/routes/auth_routes.py

from datetime import datetime
from flask import (
    Blueprint, render_template, redirect, url_for, flash, request, current_app
)
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from app.forms.login_form import LoginForm
from app.forms.registration_form import RegistrationForm
from app.forms.request_reset_form import RequestResetForm
from app.forms.reset_password_form import ResetPasswordForm
from app.utils.email import send_reset_email, verify_reset_token

auth_bp = Blueprint(
    'auth',
    __name__,
    template_folder='../templates/auth'
)



@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))  # O la ruta principal de tu app

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.activo:
            # 1) Verificar bloqueo por intentos fallidos
            if user.is_account_locked():
                flash('Cuenta bloqueada temporalmente. Intenta de nuevo más tarde.', 'danger')
                return redirect(url_for('auth.login'))

            # 2) Verificar contraseña
            if user.check_password(form.password.data):
                # Resetear contador de intentos
                user.reset_failed_attempts()
                user.ultimo_acceso = datetime.utcnow()
                db.session.commit()

                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next') or url_for('main.index')
                return redirect(next_page)
            else:
                # Contraseña incorrecta: incrementar intentos fallidos
                user.intentos_fallidos += 1
                user.ultimo_intento_fallido = datetime.utcnow()
                db.session.commit()

                if user.intentos_fallidos >= 5:
                    flash('Has excedido el máximo de intentos. Tu cuenta está bloqueada por 30 minutos.', 'warning')
                else:
                    restantes = 5 - user.intentos_fallidos
                    flash(f'Usuario o contraseña incorrectos. Te quedan {restantes} intentos.', 'danger')
        else:
            flash('Usuario no encontrado o inactivo.', 'danger')
    return render_template('login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
@login_required
# ■ Opcional: solo Administrador puede crear usuarios
# from app.utils.decorators import roles_required
# @roles_required('Administrador')
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(
            nombre=form.nombre.data,
            email=form.email.data,
            rol=form.rol.data,
            activo=True
        )
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Usuario registrado exitosamente.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)


@auth_bp.route('/reset_password', methods=['GET', 'POST'])
def request_reset():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Se ha enviado un correo con instrucciones para restablecer la contraseña.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('request_reset.html', form=form)


@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    email = verify_reset_token(token)
    if not email:
        flash('El enlace de restablecimiento no es válido o ha expirado.', 'danger')
        return redirect(url_for('auth.request_reset'))

    user = User.query.filter_by(email=email).first_or_404()
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.reset_failed_attempts()
        db.session.commit()
        flash('Tu contraseña ha sido restablecida. Ya puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('reset_password.html', form=form)
