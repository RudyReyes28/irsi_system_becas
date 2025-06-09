# app/forms/request_reset_form.py

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError, Length
from app.models.user import User

class RequestResetForm(FlaskForm):
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email(), Length(max=120)])
    submit = SubmitField('Solicitar Restablecimiento')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('No existe ningún usuario con ese correo.')
