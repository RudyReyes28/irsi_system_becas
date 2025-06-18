import pytest
from datetime import datetime, date
from app import create_app, db
from app.models.solicitante import Solicitante
from app.models.becado import Becado
from app.models.estado_becado import EstadoBecado
from app.models.historial_estado import HistorialEstado
from app.models.enums import EstadoSolicitud, EstadoBeca
from app.services.becados_service import (
    convertir_solicitante_a_becado,
    cambiar_estado_becado,
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

def make_solicitante_aprobado(session):
    s = Solicitante(
        nombre="Alice",
        emails="a@x.com",
        documento="D100",
        fecha_nacimiento=date(1995,1,1),
        genero="FEMENINO",
        pais="CHILE",
        ciudad="SCL",
        nivel_educativo="Pregrado",
        institucion="Uni",
        programa_solicitado="CIBERSEGURIDAD",
        modalidad="VIRTUAL",
        estado=EstadoSolicitud.APROBADO,
        fecha_registro=datetime.utcnow(),
        fecha_actualizacion=datetime.utcnow()
    )
    session.add(s); session.commit()
    return s

def test_convertir_solicitante_a_becado(session):
    s = make_solicitante_aprobado(session)
    bec = convertir_solicitante_a_becado(s.id, usuario_id=7)
    # Becado creado
    assert isinstance(bec, Becado)
    # estado solicitante cambiado
    s2 = session.query(Solicitante).get(s.id)
    assert s2.estado == EstadoSolicitud.CONVERTIDO
    # registro en estado_becado
    hist_b = session.query(EstadoBecado).filter_by(becado_id=bec.id).all()
    assert any(h.estado == EstadoBeca.ACTIVO and h.usuario_id == 7 for h in hist_b)
    # historial de solicitante
    hist_s = session.query(HistorialEstado).filter_by(solicitante_id=s.id).all()
    assert any(h.estado == EstadoSolicitud.CONVERTIDO for h in hist_s)

def test_cambiar_estado_becado(session):
    # primero convertir uno nuevo
    s = make_solicitante_aprobado(session)
    bec = convertir_solicitante_a_becado(s.id, usuario_id=1)
    # cambiar a SUSPENDIDO
    cambiar_estado_becado(bec.id, EstadoBeca.SUSPENDIDO, usuario_id=2, comentario="x")
    b2 = session.query(Becado).get(bec.id)
    assert b2.estado == EstadoBeca.SUSPENDIDO
    # nueva entrada en historial
    evs = session.query(EstadoBecado).filter_by(becado_id=bec.id).all()
    assert any(ev.estado == EstadoBeca.SUSPENDIDO and ev.usuario_id == 2 and ev.observacion=="x"
               for ev in evs)
