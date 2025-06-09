# app/forms/solicitante_forms.py

from flask_wtf import FlaskForm
from wtforms import (
    StringField, DateField, SelectField, TextAreaField,
    FloatField, IntegerField, DecimalField, SubmitField
)
from wtforms.validators import DataRequired, Email, Length, NumberRange
from app.models.enums import Genero, Pais, Programa, Modalidad

class SolicitanteForm(FlaskForm):
    # Paso 1: Datos Personales
    nombre = StringField(
        'Nombre completo',
        validators=[DataRequired(), Length(max=150)]
    )
    emails = StringField(
        'Correo electrónico',
        validators=[DataRequired(), Email(), Length(max=120)]
    )
    documento = StringField(
        'Documento de identidad',
        validators=[DataRequired(), Length(max=50)]
    )
    fecha_nacimiento = DateField(
        'Fecha de nacimiento',
        format='%Y-%m-%d',
        validators=[DataRequired()]
    )
    genero = SelectField(
        'Género',
        choices=[(g.name, g.value) for g in Genero],
        validators=[DataRequired()]
    )
    pais = SelectField(
        'País',
        choices=[(p.name, p.value) for p in Pais],
        validators=[DataRequired()]
    )
    ciudad = StringField(
        'Ciudad',
        validators=[DataRequired(), Length(max=100)]
    )
    telefonos = StringField(
        'Teléfono',
        validators=[DataRequired(), Length(max=20)]
    )

    # Paso 2: Información Académica
    nivel_educativo = StringField(
        'Nivel educativo',
        validators=[DataRequired(), Length(max=100)]
    )
    institucion = StringField(
        'Institución educativa',
        validators=[DataRequired(), Length(max=150)]
    )
    promedio = FloatField(
        'Promedio académico',
        validators=[DataRequired()]
    )
    experiencia_tech = TextAreaField(
        'Experiencia en tecnología',
        validators=[Length(max=500)]
    )

    # Paso 3: Datos Socioeconómicos
    situacion_laboral = StringField(
        'Situación laboral',
        validators=[DataRequired(), Length(max=100)]
    )
    ingresos = DecimalField(
        'Ingresos familiares aproximados',
        validators=[DataRequired()]
    )
    acceso_tecnologia = SelectField(
        'Acceso a tecnología',
        choices=[('Sí', 'Sí'), ('No', 'No')],
        validators=[DataRequired()]
    )
    dependientes = IntegerField(
        'Número de dependientes económicos',
        validators=[DataRequired(), NumberRange(min=0)]
    )

    # Paso 4: Información del Programa
    programa_solicitado = SelectField(
        'Programa solicitado',
        choices=[(p.name, p.value) for p in Programa],
        validators=[DataRequired()]
    )
    modalidad = SelectField(
        'Modalidad preferida',
        choices=[(m.name, m.value) for m in Modalidad],
        validators=[DataRequired()]
    )
    disponibilidad = StringField(
        'Disponibilidad horaria',
        validators=[DataRequired(), Length(max=200)]
    )
    motivacion = TextAreaField(
        'Motivación personal (500 palabras máx.)',
        validators=[DataRequired(), Length(max=500)]
    )
    objetivos = TextAreaField(
        'Objetivos profesionales (500 palabras máx.)',
        validators=[DataRequired(), Length(max=500)]
    )

    submit = SubmitField('Guardar')
