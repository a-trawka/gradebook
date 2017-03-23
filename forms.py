# from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import PasswordField
from wtforms import validators


# def flash_errors(form):
#     for field, errors in form.errors.items():
#         for error in errors:
#             flash(error)


class AdminLoginForm(FlaskForm):
    login = PasswordField('login', [validators.InputRequired()])
    pswd = PasswordField('pswd', [validators.InputRequired()])


class TeacherEditForm(FlaskForm):
    first_name = StringField('first_name', [validators.InputRequired()])
    last_name = StringField('last_name', [validators.InputRequired()])


class SubjectEditForm(FlaskForm):
    name = StringField('name', [validators.InputRequired()])


class StudentEditForm(FlaskForm):
    first_name = StringField('first_name', [validators.InputRequired()])
    last_name = StringField('last_name', [validators.InputRequired()])
    group = StringField('group', [validators.InputRequired()])


class NewStudentForm(FlaskForm):
    first_name = StringField('first_name')
    last_name = StringField('last_name')
    group = StringField('group')
    username = StringField('username',   [validators.InputRequired()])
    password = PasswordField('password', [validators.InputRequired(),
                                          validators.Length(min=4, max=70)])
    confirm = PasswordField('confirm',   [validators.InputRequired(),
                                          validators.EqualTo('password', message='Passwords do not match.')])
