import pytest
from app import create_app, db

from app.config import TestingConfig


@pytest.fixture(scope='session')
def app():
    """Crea la app con TestingConfig."""
    app = create_app(TestingConfig)
    with app.app_context():
        yield app

@pytest.fixture(scope='function')
def client(app):
    """Cliente HTTP que monta y desmonta la BD en cada test."""
    db.create_all()
    yield app.test_client()
    db.session.remove()
    db.drop_all()

@pytest.fixture(scope='function')
def runner(app):
    """Para invoke comandos CLI si quieres probar flask cli."""
    return app.test_cli_runner()

@pytest.fixture(autouse=True)
def login_client(client):
    client.post('/login', data={'email':'admin@test.com','password':'secret'})