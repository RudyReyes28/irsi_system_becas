# app/utils/email.py

import os
from flask import url_for, current_app
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message, Mail

mail = Mail()

def init_mail(app):
    mail.init_app(app)

def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='password-reset-salt')

def verify_reset_token(token, expiration=3600):
    """
    Verifica el token para restablecer contraseña.
    expiration = segundos (por defecto 1h).
    """
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt='password-reset-salt',
            max_age=expiration
        )
    except Exception:
        return None
    return email

def send_reset_email(user):
    """
    Envía un correo con enlace para restablecer contraseña.
    """
    token = generate_reset_token(user.email)
    reset_url = url_for('auth.reset_password_token', token=token, _external=True)
    msg = Message('Restablece tu contraseña',
                  sender=current_app.config.get('MAIL_USERNAME'),
                  recipients=[user.email])
    msg.body = f'''
Hola {user.nombre},

Para restablecer tu contraseña, haz clic en el siguiente enlace:
{reset_url}

Si no solicitaste este cambio, simplemente ignora este correo.

Saludos,
Equipo IRSI
'''
    mail.send(msg)
