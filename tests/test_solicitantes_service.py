import pytest
from datetime import datetime, date
from app import create_app, db
from app.models.solicitante import Solicitante
from app.models.historial_estado import HistorialEstado
from app.models.enums import EstadoSolicitud
from app.services.solicitantes_service import (
    detectar_reaplicacion,
    cambiar_estado_solicitante,
)

@pytest.fixture(scope="module")
def test_app():
    app = create_app("app.config.TestingConfig")
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def session(test_app):
    return db.session

def make_solicitante(session, **kwargs):
    s = Solicitante(
        nombre=kwargs.get("nombre", "Test"),
        emails=kwargs.get("emails", "t@x.com"),
        documento=kwargs.get("documento", "ABC123"),
        fecha_nacimiento=kwargs.get("fecha_nacimiento", date(2000,1,1)),
        genero=kwargs.get("genero", "MASCULINO"),
        pais=kwargs.get("pais", "PERU"),
        ciudad="Ciudad",
        nivel_educativo="Pregrado",
        institucion="Uni",
        programa_solicitado=kwargs.get("programa_solicitado", "PROGRAMADOR_JUNIOR"),
        modalidad=kwargs.get("modalidad", "PRESENCIAL"),
        estado=kwargs.get("estado", EstadoSolicitud.EN_REVISION),
        fecha_registro=datetime.utcnow(),
        fecha_actualizacion=datetime.utcnow()
    )
    session.add(s)
    session.commit()
    return s

def test_detectar_reaplicacion_por_email(session):
    s1 = make_solicitante(session, emails="foo@example.com", documento="D1")
    # busca substring en email
    found = detectar_reaplicacion("foo@", "X")
    assert found.id == s1.id

def test_detectar_reaplicacion_por_documento(session):
    s2 = make_solicitante(session, emails="bar@x.com", documento="DOC99")
    found = detectar_reaplicacion("no-match", "DOC99")
    assert found.id == s2.id

def test_cambiar_estado_solicitante_crea_historial(session):
    s = make_solicitante(session, estado=EstadoSolicitud.EN_REVISION)
    cambiar_estado_solicitante(s.id, EstadoSolicitud.APROBADO, usuario_id=42, comentario="ok")
    # el solicitante debe haber cambiado
    s2 = session.query(Solicitante).get(s.id)
    assert s2.estado == EstadoSolicitud.APROBADO
    # debe existir un HistorialEstado
    hist = session.query(HistorialEstado).filter_by(solicitante_id=s.id).all()
    assert any(h.estado == EstadoSolicitud.APROBADO and h.usuario_id == 42 and h.comentario == "ok"
               for h in hist)
