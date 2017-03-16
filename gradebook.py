"""Gradebook web application, by Adrian Trawka - https://github.com/a-trawka"""
from flask import Flask
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask import session
from flask import flash
from bcrypt import hashpw
from wrappers import login_required
from wrappers import guest_status_required
from wrappers import teacher_required
from wrappers import teacher_or_admin_required
from wrappers import student_required
from db_model import *
from custom_exceptions import WrongPasswordException
from admin import admin_blueprint

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'development'
app.register_blueprint(admin_blueprint, url_prefix='/admin')

db = get_db()


# begin of miscellaneous methods block
def create_tables():
    """Create database tables from models, unless they already exist."""
    db.create_tables([Student, Teacher, Subject, TeacherSubject, Grade], safe=True)


def authorize_student(student):
    session['logged_in'] = True
    session['user_id'] = student.id
    session['username'] = student.username
    session['type'] = 'S'


def authorize_teacher(teacher):
    session['logged_in'] = True
    session['user_id'] = teacher.id
    session['username'] = teacher.username
    session['type'] = 'T'


def get_current_user():
    """Returns an object of Student or Teacher class, whose credentials are currently saved in session."""
    if session['logged_in']:
        if session['type'] == 'S':
            return Student.get(Student.username == session['username'])
        elif session['type'] == 'T':
            return Teacher.get(Teacher.username == session['username'])
# end of miscellaneous methods block


@app.before_request
def before_request():
    g.db = db
    db.connect()


@app.after_request
def after_request(response):
    g.db.close()
    return response


# URL routes:
@app.route('/')
def homepage():
    return render_template('homepage.html')


@app.route('/student_login/', methods=['GET', 'POST'])
@guest_status_required
def student_login():
    if request.method == 'POST' and request.form['username']:
        try:
            student = Student.get(username=request.form['username'])
            # adequate salt is stored in the password itself
            salt_password = student.password.encode('utf-8')
            password_to_check = request.form['password'].encode('utf-8')
            password = hashpw(password_to_check, salt_password)
            if not password == salt_password:
                raise WrongPasswordException('Wrong password')
        except WrongPasswordException:
            flash('Wrong password')
        except Student.DoesNotExist:
            flash('Wrong username or password')
        else:
            authorize_student(student)
            return redirect(url_for('student_profile'))
    return render_template('student_login.html')


@app.route('/student_profile/')
@student_required
def student_profile():
    student = get_current_user()
    subjects = Subject.select()
    grades = Grade.select().where(Grade.student == student)
    return render_template('student_profile.html', student=student, subjects=subjects, grades=grades)


@app.route('/student_profile/<username>')
@teacher_or_admin_required
def student_profile_foreign(username):
    student = Student.get(Student.username == username)
    subjects = Subject.select()
    grades = Grade.select().where(Grade.student == student)
    return render_template('student_profile.html', student=student, subjects=subjects, grades=grades)


# TODO: validation of the form (if empty)
@app.route('/add_grade/', methods=['GET', 'POST'])
@teacher_required
def add_grade():
    if request.method == 'POST':
        try:
            with db.transaction():
                grade = Grade.create(
                    student=Student.get(Student.username == request.form['student_select']),
                    subject=Subject.get(Subject.name == request.form['subject_select']),
                    teacher=get_current_user(),
                    grade=request.form['grade_select']
                )
        except DatabaseError:
            flash('An error occurred while adding a grade')
        else:
            flash('Grade added')
    students = Student.select()
    subjects = Subject.select()
    return render_template('add_grade.html', students=students, subjects=subjects)


@app.route('/teacher_login/', methods=['GET', 'POST'])
@guest_status_required
def teacher_login():
    if request.method == 'POST' and request.form['username']:
        try:
            teacher = Teacher.get(username=request.form['username'])
            # adequate salt is stored in the password itself
            salt_password = teacher.password.encode('utf-8')
            password_to_check = request.form['password'].encode('utf-8')
            password = hashpw(password_to_check, salt_password)
            if not password == salt_password:
                raise WrongPasswordException()
        except WrongPasswordException:
            flash('Wrong password')
        except Teacher.DoesNotExist:
            flash('Wrong username or password')
        else:
            authorize_teacher(teacher)
            return redirect(url_for('teacher_profile'))
    return render_template('teacher_login.html')


@app.route('/teacher_profile/')
@teacher_required
def teacher_profile():
    teacher = get_current_user()
    specs = TeacherSubject.select().where(TeacherSubject.teacher == teacher)
    return render_template('teacher_profile.html', teacher=teacher, specializations=specs)


@app.route('/groups/')
@teacher_required
def groups():
    student_groups = Student.select(Student.group).distinct().order_by(Student.group.asc())
    return render_template('groups.html', student_groups=student_groups)


@app.route('/group/')
@student_required
def group():
    group_number = get_current_user().group
    students = Student.select().where(Student.group == group_number)
    return render_template('group.html', group=group_number, students=students)


@app.route('/group/<int:group_number>/')
@teacher_required
def group_foreign(group_number):
    students = Student.select().where(Student.group == group_number)
    return render_template('group.html', group=group_number, students=students)


@app.route('/logout/')
@login_required
def logout():
    """Clears all session elements."""
    for field in session:
        session[field] = None
    return redirect(url_for('homepage'))


if __name__ == '__main__':
    create_tables()
    app.run(host='0.0.0.0')
