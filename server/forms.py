from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FileField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from werkzeug.utils import secure_filename

class RegistrationForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    public_key = FileField('Public Key (PEM format)', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_public_key(self, field):
        # Ensure the file has a .pem extension
        if field.data:
            filename = secure_filename(field.data.filename)
            if not filename.endswith('.pem'):
                raise ValueError('File must be in .pem format')
