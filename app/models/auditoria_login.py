# app/models/auditoria_login.py
from datetime import datetime
from app import db

class AuditoriaLogin(db.Model):
    __tablename__ = 'auditoria_login'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    exito = db.Column(db.Boolean, nullable=False)
    ip = db.Column(db.String(45))  # IPv4 o IPv6
    user_agent = db.Column(db.String(255))

    def __repr__(self):
        estado = "Éxito" if self.exito else "Fallo"
        return f'<Login {self.user_id} {estado} - {self.fecha}>'
