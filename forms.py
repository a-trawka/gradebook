from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, DecimalField, SubmitField
from wtforms.validators import InputRequired, EqualTo, Length
from db_model import Student, Subject


_ir_msg_template = '%s field is required.'


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(error)


class AddGradeForm(FlaskForm):
    _student_query = Student.select()
    _student_options = [(student.username, student.first_name + ' ' + student.last_name) for student in _student_query]
    _student_options.insert(0, ('', ''))
    student_select = SelectField(
        'Student',
        validators=[InputRequired(message=_ir_msg_template % 'Student')],
        choices=_student_options)

    _subject_query = Subject.select()
    _subject_options = [(subject.name, subject.name) for subject in _subject_query]
    _subject_options.insert(0, ('', ''))
    subject_select = SelectField(
        'Subject',
        validators=[InputRequired(message=_ir_msg_template % 'Subject')],
        choices=_subject_options)

    grade = DecimalField('Grade', validators=[InputRequired(message=_ir_msg_template % 'Grade')])
    submit = SubmitField('Submit')


class AdminLoginForm(FlaskForm):
    login = PasswordField('ID', validators=[InputRequired(message=_ir_msg_template % 'ID')])
    pswd = PasswordField('PSWD', validators=[InputRequired(message=_ir_msg_template % 'PSWD')])
    submit = SubmitField('Log in')


class TeacherEditForm(FlaskForm):
    first_name = StringField('first_name', validators=[InputRequired(message=_ir_msg_template % 'First name')])
    last_name = StringField('last_name', validators=[InputRequired(message=_ir_msg_template % 'Last name')])
    submit = SubmitField('Save')


class SubjectEditForm(FlaskForm):
    name = StringField('name', validators=[InputRequired(message=_ir_msg_template % 'Name')])
    submit = SubmitField('Save')


class StudentEditForm(FlaskForm):
    first_name = StringField('first_name', validators=[InputRequired(message=_ir_msg_template % 'First name')])
    last_name = StringField('last_name', validators=[InputRequired(message=_ir_msg_template % 'Last name')])
    group = StringField('group', validators=[InputRequired(message=_ir_msg_template % 'Group')])
    submit = SubmitField('Save')


class NewStudentForm(FlaskForm):
    first_name = StringField('first_name')
    last_name = StringField('last_name')
    group = StringField('group')
    username = StringField('username', validators=[InputRequired(message=_ir_msg_template % 'Username')])
    password = PasswordField('password', validators=[InputRequired(message=_ir_msg_template % 'Password'),
                                                     Length(min=4, max=70)])
    confirm = PasswordField('confirm', validators=[EqualTo('password', message='Passwords do not match.')])
    submit = SubmitField('Submit')
