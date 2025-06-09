# app/models/becado.py
from datetime import datetime
from sqlalchemy.orm import relationship
from app import db
from .enums import EstadoBeca, Modalidad

class Becado(db.Model):
    __tablename__ = 'becados'

    id = db.Column(db.Integer, primary_key=True)
    solicitante_id = db.Column(db.Integer, db.ForeignKey('solicitantes.id'), unique=True, nullable=False)
    
    cohorte = db.Column(db.String(50), nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    modalidad = db.Column(db.Enum(Modalidad), nullable=False)
    sede = db.Column(db.String(100))
    plataforma_externa_id = db.Column(db.String(100))  # ID en plataforma educativa externa

    estado = db.Column(db.Enum(EstadoBeca), default=EstadoBeca.ACTIVO)
    fecha_ultimo_cambio_estado = db.Column(db.DateTime, default=datetime.utcnow)

    solicitante = relationship("Solicitante", backref=db.backref("beca", uselist=False))
    historial_estados = relationship("EstadoBecado", backref="becado", lazy=True)

    def __repr__(self):
        return f"<Becado {self.solicitante.nombre} - {self.estado.value}>"
