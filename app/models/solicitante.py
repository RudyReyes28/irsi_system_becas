# app/models/solicitante.py
from datetime import datetime
from sqlalchemy.orm import validates
from app import db
from .enums import EstadoSolicitud, Genero, Pais, Programa, Modalidad
import os
from flask import current_app

class Solicitante(db.Model):
    __tablename__ = 'solicitantes'

    id = db.Column(db.Integer, primary_key=True)

    # Datos personales
    nombre = db.Column(db.String(100), nullable=False)
    documento = db.Column(db.String(20), nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    genero = db.Column(db.Enum(Genero), nullable=False)
    pais = db.Column(db.Enum(Pais), nullable=False)
    ciudad = db.Column(db.String(100), nullable=False)
    telefonos = db.Column(db.String(100))  
    emails = db.Column(db.String(150))     

    # Info académica
    nivel_educativo = db.Column(db.String(100), nullable=False)
    institucion = db.Column(db.String(150), nullable=False)
    promedio = db.Column(db.Float, nullable=True)
    experiencia_tech = db.Column(db.Text)

    # Datos socioeconómicos
    situacion_laboral = db.Column(db.String(100))
    ingresos = db.Column(db.Float)
    acceso_tecnologia = db.Column(db.String(255))
    dependientes = db.Column(db.Integer)

    # Información del programa
    programa_solicitado = db.Column(db.Enum(Programa), nullable=False)
    modalidad = db.Column(db.Enum(Modalidad), nullable=False)
    disponibilidad = db.Column(db.String(255))
    motivacion = db.Column(db.Text)
    objetivos = db.Column(db.Text)

    # Control
    estado = db.Column(db.Enum(EstadoSolicitud), default=EstadoSolicitud.EN_REVISION)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, onupdate=datetime.utcnow)

    #historial_estados = db.relationship('HistorialEstado', backref='solicitante', lazy=True)

    def __repr__(self):
        return f'<Solicitante {self.nombre} - {self.estado.value}>'

    # Métodos útiles
    @staticmethod
    def buscar_por_documento(doc):
        return Solicitante.query.filter_by(documento=doc).first()

    @staticmethod
    def filtrar_por_estado(estado):
        return Solicitante.query.filter_by(estado=estado).all()

    @validates('promedio')
    def validar_promedio(self, key, value):
        if value is not None and (value < 0 or value > 10):
            raise ValueError("El promedio debe estar entre 0 y 10")
        return value

    @validates('emails')
    def validar_emails(self, key, value):
        if value and not all("@" in email for email in value.split(",")):
            raise ValueError("Todos los correos deben ser válidos")
        return value
    

    @staticmethod
    def buscar_avanzado(filtros: dict, page: int, per_page: int):
        query = Solicitante.query
        if filtros.get('nombre'):
            query = query.filter(Solicitante.nombre.ilike(f"%{filtros['nombre']}%"))
        if filtros.get('programa'):
            query = query.filter(Solicitante.programa_solicitado == filtros['programa'])
        if filtros.get('estado'):
            try:
                estado_enum = EstadoSolicitud[filtros['estado']]
                query = query.filter(Solicitante.estado == estado_enum)
            except KeyError:
                pass  # si no coincide, no filtrar
        if filtros.get('pais'):
            query = query.filter(Solicitante.pais == filtros['pais'])
        return query.order_by(Solicitante.fecha_registro.desc()).paginate(page=page, per_page=per_page)

    
    def listar_documentos(self):
        """
        Lista los nombres de archivos subidos para este solicitante.
        Busca en la carpeta definida por UPLOAD_FOLDER_SOLICITANTES/<id>.
        """
        upload_folder = current_app.config.get('UPLOAD_FOLDER_SOLICITANTES')
        if not upload_folder:
            return []

        carpeta = os.path.join(upload_folder, str(self.id))
        try:
            return os.listdir(carpeta)
        except FileNotFoundError:
            # Aún no hay carpeta para este solicitante
            return []
        except Exception as e:
            # Algo inesperado
            current_app.logger.error(f"Error al listar documentos en {carpeta}: {e}")
            return []
    @property
    def programa_legible(self):
        return self.programa_solicitado.name.replace("_", " ").title()

    @property
    def estado_legible(self):
        return self.estado.name.replace("_", " ").title()
