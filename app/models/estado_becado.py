# app/models/estado_becado.py
from datetime import datetime
from app import db
from .enums import EstadoBeca

class EstadoBecado(db.Model):
    __tablename__ = 'estado_becado_historial'

    id = db.Column(db.Integer, primary_key=True)
    becado_id = db.Column(db.Integer, db.ForeignKey('becados.id'), nullable=False)
    estado = db.Column(db.Enum(EstadoBeca), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    observacion = db.Column(db.String(255))

    def __repr__(self):
        return f"<EstadoBecado {self.estado.value} @ {self.fecha}>"
