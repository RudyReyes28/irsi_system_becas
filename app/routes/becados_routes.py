# app/routes/becados_routes.py
from flask import Blueprint

becados_bp = Blueprint('becados', __name__, url_prefix='/becados')

@becados_bp.route('/')
def index():
    return "Lista de becados - Por implementar"

@becados_bp.route('/nuevo')
def nuevo():
    return "Nuevo becado - Por implementar"