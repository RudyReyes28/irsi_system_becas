from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models.user import User

class UserForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=100)])
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email(check_deliverability=False), Length(max=120)])
    rol = SelectField('Rol', choices=[('Administrador','Administrador'), ('Director','Director'), ('Asistente','Asistente'), ('Consulta','Consulta')], validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[Length(min=8, message='Mínimo 8 caracteres'), EqualTo('confirm_password', message='Las contraseñas deben coincidir')])
    confirm_password = PasswordField('Confirmar Contraseña')
    activo = BooleanField('Activo')
    submit = SubmitField('Guardar')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user and (not self._obj or user.id != getattr(self._obj, 'id', None)):
            raise ValidationError('Este correo ya está en uso.')

class PasswordResetForm(FlaskForm):
    password = PasswordField('Nueva Contraseña', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password', message='Las contraseñas deben coincidir')])
    submit = SubmitField('Restablecer')