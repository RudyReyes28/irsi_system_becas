#!/usr/bin/env python3
import os
from app import create_app
from app.config import config
import requests

# Obtener el entorno desde variable de entorno o usar 'development' por defecto
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config[config_name])

ip = requests.get("https://api.ipify.org").text
print(f"🔎 IP pública: {ip}")


if __name__ == '__main__':
    app.run(
        host='0.0.0.0', # nosec B104
        port=int(os.environ.get('PORT', 5000)),
        debug=app.config.get('DEBUG', False)
    )