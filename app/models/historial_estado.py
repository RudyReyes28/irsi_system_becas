from datetime import datetime
from app import db
from .enums import EstadoSolicitud

class HistorialEstado(db.Model):
    __tablename__ = 'historial_estados'

    id = db.Column(db.Integer, primary_key=True)
    solicitante_id = db.Column(db.Integer, db.ForeignKey('solicitantes.id'), nullable=False)
    usuario_id    = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)          # <–– Nueva columna
    estado        = db.Column(db.Enum(EstadoSolicitud), nullable=False)
    fecha         = db.Column(db.DateTime, default=datetime.utcnow)
    
    comentario    = db.Column(db.String(255), nullable=True)                                                # Renombrado

    # Relaciones
    solicitante = db.relationship('Solicitante', backref=db.backref('historial_estados', lazy='dynamic'))
    usuario     = db.relationship('User',       backref=db.backref('cambios_estado', lazy='dynamic'))

    def __repr__(self):
        return f'<Estado {self.estado.value} para solicitante {self.solicitante_id} por usuario {self.usuario_id} en {self.fecha}>'
