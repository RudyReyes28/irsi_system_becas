# seeds.py
import os
from app import create_app, db
from app.models.user import User
from app.config import config
def seed_users():
    """
    Inserta usuarios base en la base de datos para pruebas.
    Cambia emails, nombres y contraseñas según necesites.
    """

    # Instanciamos la app en modo 'development' (o el que uses)
    config_name = os.environ.get('FLASK_ENV', 'development')
    app = create_app(config[config_name])
    with app.app_context():
        # Lista de usuarios base que queremos crear:
        usuarios_base = [
            {
                "nombre": "Admin IR Si",
                "email": "admin@example.com",
                "password": "Admin123!",
                "rol": "Administrador"
            },
            {
                "nombre": "Director Programas",
                "email": "director@example.com",
                "password": "Director123!",
                "rol": "Director"
            },
            {
                "nombre": "Asistente Operativo",
                "email": "asistente@example.com",
                "password": "Asistente123!",
                "rol": "Asistente"
            },
            {
                "nombre": "Usuario Consulta",
                "email": "consulta@example.com",
                "password": "Consulta123!",
                "rol": "Consulta"
            },
        ]

        created = 0
        for udata in usuarios_base:
            # Verificamos si ya existe el email para evitar duplicados
            existe = User.query.filter_by(email=udata["email"]).first()
            if existe:
                print(f"> Ya existe {udata['email']}, se omite.")
                continue

            u = User(
                nombre=udata["nombre"],
                email=udata["email"],
                rol=udata["rol"],
                activo=True
            )
            u.set_password(udata["password"])
            db.session.add(u)
            created += 1

        if created:
            db.session.commit()
            print(f">> Se crearon {created} usuarios base.")
        else:
            print(">> No se crearon usuarios nuevos (ya existían).")

if __name__ == "__main__":
    seed_users()
