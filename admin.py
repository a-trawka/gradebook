from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask import session
from flask import flash
from bcrypt import hashpw
from bcrypt import gensalt
from db_model import *
from wrappers import guest_status_required
from wrappers import admin_required

admin_blueprint = Blueprint('admin_blueprint', 'admin_blueprint')


def authorize_admin():
    session['logged_in'] = True
    session['type'] = 'X'


@admin_blueprint.route('/login/', methods=['GET', 'POST'])
@guest_status_required
def admin_login():
    if request.method == 'POST':
        if request.form['id'] == 'test' and request.form['pswd'] == 'test':
            authorize_admin()
            return redirect(url_for('homepage'))
        else:
            flash('NOPE')
    return render_template('admin_login.html')


@admin_blueprint.route('/new_student/', methods=(['GET', 'POST']))
@admin_required
def new_student():
    if request.method == 'POST' and request.form['username'] and len(request.form['password']) <= 70:
        try:
            with db.transaction():
                student = Student.create(
                    first_name=request.form['first_name'],
                    last_name=request.form['last_name'],
                    group=request.form['group'],
                    username=request.form['username'],
                    password=hashpw(request.form['password'].encode('utf-8'), gensalt())
                )
        except IntegrityError:
            flash('Username already taken')
        except DatabaseError:
            flash('An error occurred while creating a student')
        else:
            flash('Student added')
    return render_template('new_student.html')


@admin_blueprint.route('/new_teacher/', methods=['GET', 'POST'])
@admin_required
def new_teacher():
    if request.method == 'POST' and request.form['username'] and len(request.form['password']) <= 70:
        try:
            with db.transaction():
                teacher = Teacher.create(
                    first_name=request.form['first_name'],
                    last_name=request.form['last_name'],
                    username=request.form['username'],
                    password=hashpw(request.form['password'].encode('utf-8'), gensalt())
                )
        except IntegrityError:
            flash('Username already taken')
        except DatabaseError:
            flash('An error occurred while creating a teacher')
        else:
            flash('Teacher created')
    return render_template('new_teacher.html')


# method DELETE???
@admin_blueprint.route('/teacher_profile/<username>/', methods=['GET', 'POST'])
@admin_required
def teacher_profile(username):
    teacher = Teacher.get(Teacher.username == username)
    if request.method == 'POST':
        if teacher.delete_instance():
            flash('Teacher deleted.')
            return redirect(url_for('admin_blueprint.admin_teachers'))
        flash('Something went wrong while trying to delete a record.')
    specs = TeacherSubject.select().where(TeacherSubject.teacher == teacher)
    return render_template('teacher_profile.html', teacher=teacher, specializations=specs)


@admin_blueprint.route('/add_specialization/<username>/', methods=['GET', 'POST'])
@admin_required
def add_specialization(username):
    if request.method == 'POST':
        try:
            with db.transaction():
                spec = TeacherSubject.get_or_create(
                    teacher=Teacher.get(Teacher.username == username),
                    specialization=Subject.get(Subject.name == request.form['subject_select'])
                )
        except DatabaseError:
            flash('An error occurred, try again')
        else:
            flash('Specialization added')
    subs = Subject.select()
    teacher = Teacher.get(Teacher.username == username)
    return render_template('add_specialization.html', teacher=teacher, subjects=subs)


@admin_blueprint.route('/add_subject/', methods=['GET', 'POST'])
@admin_required
def add_subject():
    if request.method == 'POST':
        try:
            with db.transaction():
                subject = Subject.create(name=request.form['name'])
        except DatabaseError:
            flash('An error occured, try again.')
        else:
            flash('Subject added.')
    return render_template('add_subject.html')


@admin_blueprint.route('/students/')
@admin_required
def admin_students():
    students = Student.select()
    return render_template('admin_students.html', students=students)


@admin_blueprint.route('/teachers/')
@admin_required
def admin_teachers():
    teachers = Teacher.select()
    return render_template('admin_teachers.html', teachers=teachers)


@admin_blueprint.route('/subjects')
@admin_required
def admin_subjects():
    subjects = Subject.select()
    return render_template('admin_subjects.html', subjects=subjects)
