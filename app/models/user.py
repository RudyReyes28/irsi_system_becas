# app/models/user.py

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    rol = db.Column(db.String(20), nullable=False)  # Administrador, Director, Asistente, Consulta
    activo = db.Column(db.Boolean, default=True)

    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_acceso = db.Column(db.DateTime, nullable=True)

    intentos_fallidos = db.Column(db.Integer, default=0)
    ultimo_intento_fallido = db.Column(db.DateTime, nullable=True)

    # Relación con auditoría de logins (si la tienes)
    accesos = db.relationship('AuditoriaLogin', backref='usuario', lazy=True)

    def set_password(self, password):
        """Hashea la contraseña usando bcrypt/pbkdf2:sha256."""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        """Verifica la contraseña hasheada."""
        return check_password_hash(self.password_hash, password)

    def has_role(self, role):
        """Verifica si el usuario tiene el rol especificado."""
        return self.rol.lower() == role.lower()

    def has_any_role(self, roles: list):
        """Verifica si el usuario tiene alguno de los roles dados."""
        return self.rol.lower() in [r.lower() for r in roles]

    def is_account_locked(self):
        """
        Retorna True si el usuario ha excedido 5 intentos fallidos
        y el último intento está dentro de los últimos 30 minutos.
        """
        from datetime import datetime, timedelta

        if self.intentos_fallidos >= 5 and self.ultimo_intento_fallido:
            return datetime.utcnow() < (self.ultimo_intento_fallido + timedelta(minutes=30))
        return False

    def reset_failed_attempts(self):
        self.intentos_fallidos = 0
        self.ultimo_intento_fallido = None

    def __repr__(self):
        return f'<User {self.email} ({self.rol})>'
