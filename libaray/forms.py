from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, TextAreaField, FileField, DateField, IntegerField
from wtforms.validators import Email, DataRequired, EqualTo, Length


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired('Username field is required')])
    email = StringField('Email',
                        validators=[DataRequired('Email field is required'), Email('Email is InValid')])
    password = PasswordField('Password',
                             validators=[DataRequired('Password field is required'),
                                         Length(min=6, message='Your password is less than 6 characters')])
    confirm_password = PasswordField('Password',
                                     validators=[DataRequired('Password field is required'),
                                                 Length(min=6,
                                                        message='Your confirm password is less than 6 '
                                                                'characters'),
                                                 EqualTo('password',
                                                         'Password Confirm is not same with password')])
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired('Email field is required'), Email('Email is InValid')])
    password = PasswordField('Password',
                             validators=[DataRequired('Password field is required'),
                                         Length(min=6, message='Your password is less than 6 characters')])
    submit = SubmitField('Log In')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired('Username field is required')])
    email = StringField('Email',
                        validators=[DataRequired('Email field is required'), Email('Email is InValid')])
    submit = SubmitField('Edit')


class ChangePasswordForm(FlaskForm):
    oldPassword = PasswordField('oldPassword',
                                validators=[DataRequired('Password field is required'),
                                            Length(min=6, message='Your password is less than 6 characters')])

    newPassword = PasswordField('newPassword',
                                validators=[DataRequired('New Password field is required'),
                                            Length(min=6, message='Your password is less than 6 characters')])

    confirm_password = PasswordField('confirmPassword',
                                     validators=[DataRequired('Confirm Password field is required'),
                                                 Length(min=6,
                                                        message='Your confirm password is less than 6 '
                                                                'characters'),
                                                 EqualTo('newPassword',
                                                         'Password Confirm is not same with New Password')])
    submit = SubmitField('Change Password')


class AddBookForm(FlaskForm):
    name = StringField('Title', validators=[DataRequired('Title field is required')])
    description = TextAreaField('Content', validators=[DataRequired('Description field is required')])

    thumbnail = FileField()

    publish_at = DateField('published_at')

    author = StringField('Author')

    quantity = IntegerField('quantity')

    submit = SubmitField('Add Book')


class EditBookForm(FlaskForm):
    name = StringField('Title', validators=[DataRequired('Title field is required')])

    thumbnail = FileField()

    submit = SubmitField('Edit Book')
