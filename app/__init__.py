import os
import logging
from datetime import datetime, timedelta

from flask import Flask, session, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user, logout_user
from dotenv import load_dotenv
from app.utils.email import init_mail
from app.utils.authorization import has_permission
# Cargar variables de entorno
load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app(config_class):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    init_mail(app)
    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'

    # Importar todos los modelos DESPUÉS de inicializar db
    # Esto es crucial para que Flask-Migrate pueda detectar los modelos
    with app.app_context():
        from app.models import all_models

        # Importaciones explícitas (opcional)
        from app.models.user import User
        from app.models.solicitante import Solicitante
        from app.models.becado import Becado
        from app.models.historial_estado import HistorialEstado
        from app.models.estado_becado import EstadoBecado
        from app.models.auditoria_login import AuditoriaLogin
        from app.models.auditoria_actividad import AuditoriaActividad
        from app.models.enums import (
            EstadoSolicitud,
            Genero,
            Pais,
            Programa,
            Modalidad,
            EstadoBeca,
        )
        from app.models.auditoria import auditar_cambio

    # Registrar blueprints/rutas
    register_routes(app)

    # Registramos context processor para permisos
    @app.context_processor
    def inject_permissions():
        """
        Inyecta en las plantillas:
         - current_role      : rol del usuario actual (o None).
         - has_perm         : función que recibe una clave de permiso y retorna True/False.
        """
        role = None
        if current_user.is_authenticated:
            role = current_user.rol
        return {
            'current_role': role,
            'has_perm': has_permission
        }
    
    setup_logging(app)

    # Middleware para timeout de sesión (2 horas)
    @app.before_request
    def session_timeout():
        if current_user.is_authenticated:
            now = datetime.utcnow()
            last_activity_raw = session.get('last_activity')

            try:
                # Convertir solo si es string
                if isinstance(last_activity_raw, str):
                    last_activity = datetime.fromisoformat(last_activity_raw)
                elif isinstance(last_activity_raw, datetime):
                    last_activity = last_activity_raw
                else:
                    last_activity = now  # fallback seguro

                elapsed = now - last_activity

                if elapsed > timedelta(hours=2):
                    logout_user()
                else:
                    session['last_activity'] = now.isoformat()

            except Exception as e:
                # En caso de error inesperado, reinicia el timestamp
                session['last_activity'] = now.isoformat()

    # Configurar logging
    setup_logging(app)
    # Registrar manejadores de errores
    register_errorhandlers(app)

    return app

def register_errorhandlers(app):
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('403.html'), 403

    @app.errorhandler(401)
    def unauthorized(error):
        # Opcional: si usas login_required, podrías redirigir a login
        return redirect(url_for('auth.login'))

@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User

    return User.query.get(int(user_id))


def register_routes(app):
    """Registra todas las rutas de la aplicación"""
    from app.routes.auth_routes import auth_bp
    #from app.routes.solicitantes_routes import solicitantes_bp
    from app.routes.becados_routes import becados_bp
    from app.routes.users import users_bp
    from app.routes.main import main_bp
    from app.routes.solicitantes import solicitantes_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(solicitantes_bp, url_prefix='/solicitantes')
    app.register_blueprint(becados_bp)
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(main_bp)


def setup_logging(app):
    log_level = app.config.get("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=log_level)
    handler = logging.StreamHandler()
    handler.setLevel(log_level)
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
