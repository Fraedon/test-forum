from flask_wtf import FlaskForm
from wtforms import Field, PasswordField, StringField, SubmitField, \
    ValidationError
from wtforms.validators import DataRequired, Email, EqualTo

from forum.models import User


class RegisterForm(FlaskForm):
    display_name = StringField("Display name", validators=[DataRequired()])
    email = StringField("Email address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm password",
                                     validators=[DataRequired(),
                                                 EqualTo("password")])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField("Email address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

    @staticmethod
    def validate_email(form: FlaskForm, field: Field) -> None:
        try:
            assert User.query.filter_by(email=field.data).first() is not None
        except:
            raise ValidationError("User not found")

    @staticmethod
    def validate_password(form: FlaskForm, field: Field) -> None:
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None:
            try:
                assert user.check_password(field.data)
            except:
                raise ValidationError("Invalid password")
