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
from forms import NewStudentForm
from forms import TeacherEditForm
from forms import SubjectEditForm
from forms import AdminLoginForm
from forms import flash_errors
from wrappers import guest_status_required
from wrappers import admin_required

admin_blueprint = Blueprint('admin_blueprint', 'admin_blueprint')


def authorize_admin():
    session['logged_in'] = True
    session['type'] = 'X'


@admin_blueprint.route('/login/', methods=['GET', 'POST'])
@guest_status_required
def admin_login():
    form = AdminLoginForm()
    if form.validate_on_submit():
        # temporary 'test'/'test'
        if form.login.data == 'test' and form.pswd.data == 'test':
            authorize_admin()
            return redirect(url_for('homepage'))
        else:
            flash('NOPE')
    return render_template('admin_login.html', form=form)


@admin_blueprint.route('/new_student/', methods=(['GET', 'POST']))
@admin_required
def new_student():
    form = NewStudentForm()
    if form.validate_on_submit():
        try:
            with db.transaction():
                student = Student.create(
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    group=form.group.data,
                    username=form.username.data,
                    password=hashpw(form.password.data.encode('utf-8'), gensalt())
                )
        except IntegrityError:
            flash('Username already taken')
        except DatabaseError:
            flash('An error occurred while creating a student')
        else:
            flash(student.username + ' student created.')
            return redirect(url_for('admin_blueprint.admin_students'))
    return render_template('new_student.html', form=form)


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


@admin_blueprint.route('/teacher_profile/<username>/', methods=['GET', 'POST'])
@admin_required
def teacher_profile(username):
    teacher = Teacher.get(Teacher.username == username)
    if request.method == 'POST':
        with db.transaction():
            if teacher.delete_instance(recursive=True):
                flash(teacher.username + ' deleted.')
                return redirect(url_for('admin_blueprint.admin_teachers'))
            flash('Something went wrong while trying to delete a record.')
    specs = TeacherSubject.select().where(TeacherSubject.teacher == teacher)
    return render_template('teacher_profile.html', teacher=teacher, specializations=specs)


@admin_blueprint.route('/teacher_profile/<username>/edit', methods=['GET', 'POST'])
@admin_required
def teacher_edit(username):
    form = TeacherEditForm()
    teacher = Teacher.get(Teacher.username == username)
    if form.validate_on_submit():
        with db.transaction():
            teacher.first_name = form.first_name.data
            teacher.last_name = form.last_name.data
            if teacher.save():
                flash(teacher.username + ' updated.')
            else:
                flash('Something went wrong.')
        return redirect(url_for('admin_blueprint.admin_teachers'))
    return render_template('teacher_edit.html', teacher=teacher, form=form)


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
            flash('An error occurred, try again.')
        else:
            flash('Subject added.')
    return render_template('add_subject.html')


@admin_blueprint.route('/subject/<name>/', methods=['POST'])
@admin_required
def subject(name):
    subj = Subject.get(Subject.name == name)
    if subj.delete_instance(recursive=True):  # delete instance and all its' occurrences as foreign fields
        flash(subj.name + ' subject has been removed.')
    else:
        flash('Something went wrong.')
    return redirect(url_for('admin_blueprint.admin_subjects'))


@admin_blueprint.route('/subject/<name>/edit/', methods=['GET', 'POST'])
@admin_required
def subject_edit(name):
    form = SubjectEditForm()
    subject = Subject.get(Subject.name == name)
    if form.validate_on_submit():
        with db.transaction():
            subject.name = form.name.data
            if subject.save():
                flash(subject.name + ' subject updated.')
            else:
                flash('Something went wrong.')
        return redirect(url_for('admin_blueprint.admin_subjects'))
    return render_template('subject_edit.html', subject=subject, form=form)


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
