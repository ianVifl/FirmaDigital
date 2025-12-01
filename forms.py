from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FileField, SelectMultipleField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from models import Usuario

class RegistrationForm(FlaskForm):
    nombre = StringField('Nombre Completo', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrarme')

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError('Ese email ya está registrado. Por favor, elige otro.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember = BooleanField('Recuérdame')
    submit = SubmitField('Iniciar Sesión')

# --- NUEVO FORMULARIO ---
class UploadDocumentForm(FlaskForm):
    documento = FileField('Seleccionar Documento (PDF)', validators=[DataRequired()])
    # coerce=int convierte la selección (que llega como texto) a número (ID del usuario)
    firmantes = SelectMultipleField('Seleccionar Firmantes', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Subir y Enviar a Firmar')