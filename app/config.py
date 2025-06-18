import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))
class Config:
    """Configuración base"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'tu-clave-secreta-aqui'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER_SOLICITANTES = os.path.join(BASE_DIR, '..', 'uploads', 'solicitantes')
    MAIL_SERVER      = os.getenv("MAIL_SERVER")
    MAIL_PORT        = int(os.getenv("MAIL_PORT", 25))
    MAIL_USE_TLS     = os.getenv("MAIL_USE_TLS", "False") == "True"
    MAIL_USE_SSL     = os.getenv("MAIL_USE_SSL", "False") == "True"
    MAIL_USERNAME    = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD    = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = tuple(os.getenv("MAIL_DEFAULT_SENDER").split(","))

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///becas_irsi_dev.db'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER_SOLICITANTES = os.path.join(BASE_DIR, '..', 'uploads', 'solicitantes')

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://usuario:password@localhost/becas_irsi'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER_SOLICITANTES = os.path.join(BASE_DIR, '..', 'uploads', 'solicitantes')

class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    WTF_CSRF_ENABLED = False          # desactiva CSRF en tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LOGIN_DISABLED = True

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}