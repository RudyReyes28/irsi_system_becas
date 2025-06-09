from app.models.solicitante import Solicitante
from sqlalchemy import or_


def existe_solicitante(email: str, documento: str) -> bool:
    """
    Verifica si ya existe un solicitante con el mismo email o documento.
    """
    return Solicitante.query.filter(or_(Solicitante.email == email,
                                        Solicitante.documento == documento)).first() is not None