from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, DecimalField, SubmitField
from wtforms.validators import InputRequired, EqualTo, Length
from model import Student, Subject

_ir_msg_template = '%s field is required.'
_l_msg_template = '%s field has to be %d-%d characters long.'


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(error)


class AddSubjectForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(message=_ir_msg_template % 'Name')])
    submit = SubmitField('Submit')


class SubjectEditForm(FlaskForm):
    name = StringField('Name of the subject', validators=[InputRequired(message=_ir_msg_template % 'Name')])
    submit = SubmitField('Save')


class AdminLoginForm(FlaskForm):
    login = PasswordField('ID', validators=[InputRequired(message=_ir_msg_template % 'ID')])
    pswd = PasswordField('PSWD', validators=[InputRequired(message=_ir_msg_template % 'PSWD')])
    submit = SubmitField('Log in')


class NewTeacherForm(FlaskForm):
    first_name = StringField('First name', validators=[InputRequired(message=_ir_msg_template % 'First name')])
    last_name = StringField('Last name', validators=[InputRequired(message=_ir_msg_template % 'Last name')])
    username = StringField('Username', validators=[InputRequired(message=_ir_msg_template % 'First name')])
    password = PasswordField('Password', validators=[Length(min=4, max=70, message=_l_msg_template % ('Password', 4, 70))])
    confirm = PasswordField('Confirm password', validators=[EqualTo('password', message='Passwords do not match.')])
    submit = SubmitField('Submit')


class TeacherEditForm(FlaskForm):
    first_name = StringField('First name', validators=[InputRequired(message=_ir_msg_template % 'First name')])
    last_name = StringField('Last name', validators=[InputRequired(message=_ir_msg_template % 'Last name')])
    submit = SubmitField('Save')


class TeacherLoginForm(FlaskForm):
    username = StringField('Username')
    # username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[Length(min=4, max=70, message=_l_msg_template % ('Password', 4, 70))])
    submit = SubmitField('Login')


class NewStudentForm(FlaskForm):
    first_name = StringField('First name')
    last_name = StringField('Last name')
    group = StringField('Group')
    username = StringField('Username', validators=[InputRequired(message=_ir_msg_template % 'Username')])
    password = PasswordField('Password', validators=[Length(min=4, max=70, message=_l_msg_template % ('Password', 4, 70))])
    confirm = PasswordField('Confirm password', validators=[EqualTo('password', message='Passwords do not match.')])
    submit = SubmitField('Submit')


class StudentEditForm(FlaskForm):
    first_name = StringField('first_name', validators=[InputRequired(message=_ir_msg_template % 'First name')])
    last_name = StringField('last_name', validators=[InputRequired(message=_ir_msg_template % 'Last name')])
    group = StringField('group', validators=[InputRequired(message=_ir_msg_template % 'Group')])
    submit = SubmitField('Save')


class StudentLoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(message=_ir_msg_template % 'Username')])
    password = PasswordField('Password', validators=[Length(min=4, max=70, message=_l_msg_template % ('Password', 4, 70))])
    submit = SubmitField('Login')


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
    _subject_options.insert(0, ('', ''))  # add first empty option
    subject_select = SelectField(
        'Subject',
        validators=[InputRequired(message=_ir_msg_template % 'Subject')],
        choices=_subject_options)

    grade = DecimalField('Grade', validators=[InputRequired(message=_ir_msg_template % 'Grade')])
    submit = SubmitField('Submit')


class AddSpecializationForm(FlaskForm):
    _subject_query = Subject.select()
    _subject_options = [(subject.name, subject.name) for subject in _subject_query]
    _subject_options.insert(0, ('', ''))
    subject_select = SelectField(
        'Subject',
        validators=[InputRequired(message=_ir_msg_template % 'Subject')],
        choices=_subject_options)
    submit = SubmitField('Submit')