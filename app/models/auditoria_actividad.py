# app/models/auditoria_actividad.py
from datetime import datetime
from app import db

class AuditoriaActividad(db.Model):
    __tablename__ = 'auditoria_actividad'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    tabla_afectada = db.Column(db.String(100), nullable=False)
    operacion = db.Column(db.String(20), nullable=False)  # CREATE, UPDATE, DELETE
    id_registro = db.Column(db.Integer, nullable=False)

    datos_antes = db.Column(db.Text)
    datos_despues = db.Column(db.Text)

    ip = db.Column(db.String(45))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Auditoría {self.operacion} en {self.tabla_afectada} por usuario {self.usuario_id}>"
