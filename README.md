# IRSI Becas System

Sistema completo para la gestión de solicitantes y becados del programa IRSI.

---

## 📂 Estructura del proyecto

```
.
├── .env.example              # Ejemplo de variables de entorno
├── database_creation.sql     # Script SQL para crear la base de datos y esquemas
├── migrations/               # Directorio Alembic con las migraciones versionadas
├── seeds.py                  # Script para poblar datos iniciales (roles, admin, etc.)
├── requirements.txt          # Dependencias Python
├── run.py                    # Entry point de Flask
├── README.md                 # Este archivo
└── app/
    ├── config.py             # Configuración de Flask
    ├── __init__.py           # Factory `create_app`
    ├── models/               # Todos los modelos SQLAlchemy
    ├── services/             # Lógica de negocio (solicitantes, becados, etc.)
    ├── routes/               # Blueprints (auth, solicitantes, becados, main, users…)
    ├── forms/                # WTForms para registro, login, solicitantes…
    ├── templates/            # Plantillas Jinja2
    └── static/               # Recursos estáticos (JS, CSS, imágenes)
```

---

## 🔧 Prerrequisitos

- **Python 3.10+**
- **Microsoft SQL Server** (o SQL Server Express)
- Cliente ODBC “ODBC Driver 17 for SQL Server”
- `pip` o `poetry`
- (Opcional) crear un entorno virtual:

  ```bash
  python -m venv .venv
  source .venv/bin/activate  # macOS/Linux
  .venv\Scripts\activate     # Windows
  ```

---

## ⚙️ Configuración de entorno

1. Copia y renombra el fichero de ejemplo:

   ```bash
   cp .env.example .env
   ```

2. Edita `.env` y define:
   ```dotenv
   FLASK_ENV=development
   SECRET_KEY=UnaClaveSuperSecreta
   SQLALCHEMY_DATABASE_URI=mssql+pyodbc://user:pass@host:port/DBName?driver=ODBC+Driver+17+for+SQL+Server
   UPLOAD_FOLDER_SOLICITANTES=/ruta/absoluta/uploads/solicitantes
   MAIL_SERVER=smtp.midominio.com
   MAIL_PORT=587
   MAIL_USERNAME=tu@correo.com
   MAIL_PASSWORD=tu_password
   MAIL_USE_TLS=True
   ```

---

## 🛠️ Instalación de dependencias

```bash
pip install -r requirements.txt
```

---

## 🗄️ 1) Crear la base de datos

1. Abre SSMS o Azure Data Studio y conéctate a tu servidor.
2. Ejecuta:

   ```sql
   :r ./database_creation.sql
   ```

   Esto crea la base de datos.
   Despues genera los permisos para realizar la conexion

---

## 🗄️ 2) Migraciones con Alembic

Las migraciones ya están generadas bajo `migrations/versions`. Para aplicar:

```bash
flask db upgrade
```

> **Si partes de cero** (base vacía, quieres regenerar):
> ```bash
> rm -rf migrations/versions/*
> flask db revision --autogenerate -m "Initial"
> flask db upgrade
> ```

---

## 🌱 3) Cargar datos de prueba (seeds)

Para poblar roles, usuario admin, cohorte demo:

```bash
python seeds.py
```

---

## ⚡ 4) Ejecutar la aplicación

Define la variable de entorno y arranca:

```bash
export FLASK_APP=run.py
export FLASK_ENV=development   # hot‑reload & debug
flask run
o
python run
```

Accede en tu navegador a:  http://localhost:5000

---

## 🔑 Acceso inicial

- **Email:** `admin@example.com`
- **Password:** `Admin123!`

---

## 📋 Rutas principales

| Ruta                       | Método | Descripción                                |
|----------------------------|--------|--------------------------------------------|
| `/login`                   | GET/POST | Iniciar sesión                          |
| `/register`                | GET/POST | Registrar usuario                       |
| `/solicitantes/`           | GET    | Listar solicitantes                       |
| `/solicitantes/create`     | GET/POST | Crear nuevo solicitante                 |
| `/solicitantes/<id>`       | GET    | Ver detalle (historial, documentos…)      |
| `/solicitantes/<id>/edit`  | GET/POST | Editar datos del solicitante            |
| `/solicitantes/<id>/change_state` | POST | Cambiar estado (modal)             |
| `/solicitantes/reaplicaciones` | GET | Listar reaplicaciones                   |
| `/solicitantes/reportes`   | GET    | Reportes gráficos y tablas                |
| `/becados/`                | GET    | Listar becados activos                    |
| `/becados/todos`           | GET    | Listar todos los becados                  |
| `/becados/convert/<id>`    | POST   | Convertir solicitante a becado            |
| `/becados/<id>`            | GET    | Detalle becado (timeline, comunicaciones) |
| `/becados/<id>/change_state` | POST | Cambiar estado de becado                |
| `/becados/communications/<id>` | GET/POST | Panel de comunicaciones            |

---

## 🧪 Tests

Si tienes tests bajo `tests/`:

```bash
pip install pytest
pytest
```

---

## 🚀 Despliegue

- Usar **Gunicorn** / **uWSGI** detrás de **NGINX**.
- Variables de entorno en producción (`FLASK_ENV=production`).
- Asegurar `SECRET_KEY` y credenciales.
- Pipeline CI/CD que:
  1. Instale dependencias
  2. Ejecute migraciones (`flask db upgrade`)
  3. Aplique seeds si procede
  4. Arranque el servicio

---

## 🤝 Contribuir

1. Haz **fork** y crea una rama `feature/tu-descripción`.
2. Agrega tests y documenta los cambios.
3. Abre un **Pull Request** detallando la funcionalidad.

---

## 📜 Licencia

Este proyecto está bajo la **MIT License**. ¡Siéntete libre de usarlo y adaptarlo!

---

**¡Bienvenido al equipo de desarrollo de IRSI Becas!**