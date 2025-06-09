# app/models/enums.py
import enum

class EstadoSolicitud(enum.Enum):
    REGISTRADO = 'Registrado'
    EN_REVISION = 'En revisión'
    APROBADO = 'Aprobado'
    RECHAZADO = 'Rechazado'
    INCOMPLETO = 'Incompleto'
    CANCELADO = 'Cancelado'

class Genero(enum.Enum):
    MASCULINO = 'Masculino'
    FEMENINO = 'Femenino'
    OTRO = 'Otro'
    NO_ESPECIFICA = 'Prefiere no decirlo'

class Pais(enum.Enum):
    # Lista de países de América Latina
    ARGENTINA = 'Argentina'
    BOLIVIA = 'Bolivia'
    CHILE = 'Chile'
    COLOMBIA = 'Colombia'
    ECUADOR = 'Ecuador'
    MEXICO = 'México'
    PERU = 'Perú'
    URUGUAY = 'Uruguay'
    VENEZUELA = 'Venezuela'
    GUATEMALA = 'Guatemala'
    HONDURAS = 'Honduras'
    EL_SALVADOR = 'El Salvador'
    NICARAGUA = 'Nicaragua'
    COSTA_RICA = 'Costa Rica'
    PANAMA = 'Panamá'
    CUBA = 'Cuba'
    REPUBLICA_DOMINICANA = 'República Dominicana'
    PARAGUAY = 'Paraguay'
    PUERTO_RICO = 'Puerto Rico'




class Programa(enum.Enum):
    PROGRAMADOR_JUNIOR = 'Programador Junior'
    CIBERSEGURIDAD = 'Ciberseguridad'

class Modalidad(enum.Enum):
    PRESENCIAL = 'Presencial'
    VIRTUAL = 'Virtual'
    HIBRIDA = 'Híbrida'

class EstadoBeca(enum.Enum):
    ACTIVO = 'Activo'
    EN_PAUSA = 'En pausa'
    DESERTOR = 'Desertor'
    GRADUADO = 'Graduado'
    SUSPENDIDO = 'Suspendido'