from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask import session
from flask import flash
from bcrypt import hashpw
from bcrypt import gensalt
from model import *
from forms import AddSubjectForm, AddSpecializationForm, NewStudentForm, StudentEditForm, TeacherEditForm, SubjectEditForm, AdminLoginForm, NewTeacherForm
from forms import flash_errors
from wrappers import guest_status_required, admin_required

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
    flash_errors(form)
    return render_template('admin_login.html', form=form)


@admin_blueprint.route('/new_student/', methods=(['GET', 'POST']))
@admin_required
def new_student():
    form = NewStudentForm()
    if form.validate_on_submit():
        try:
            with get_db()().transaction():
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
    flash_errors(form)
    return render_template('new_student.html', form=form)


@admin_blueprint.route('/student_profile/<username>/', methods=['GET', 'POST'])
@admin_required
def student_profile(username):
    student = Student.get(Student.username == username)
    if request.method == 'POST':  # removing
        with get_db().transaction():
            if student.delete_instance(recursive=True):
                flash(student.username + ' deleted.')
                return redirect(url_for('admin_blueprint.admin_students'))
            flash('Something went wrong.')
    subjects = Subject.select()
    grades = Grade.select().where(Grade.student == student)
    return render_template('student_profile.html', student=student, subjects=subjects, grades=grades)


@admin_blueprint.route('/student_profile/<username>/edit/', methods=['GET', 'POST'])
@admin_required
def student_edit(username):
    student = Student.get(Student.username == username)
    form = StudentEditForm(first_name=student.first_name, last_name=student.last_name, group=student.group)
    if form.validate_on_submit():
        with get_db().transaction():
            student.first_name = form.first_name.data
            student.last_name = form.last_name.data
            student.group = form.group.data
            if student.save():
                flash(student.username + ' edited.')
                return redirect(url_for('admin_blueprint.admin_students'))
            else:
                flash('Something went wrong.')
    flash_errors(form)
    return render_template('student_edit.html', student=student, form=form)


@admin_blueprint.route('/new_teacher/', methods=['GET', 'POST'])
@admin_required
def new_teacher():
    form = NewTeacherForm()
    if form.validate_on_submit():
        try:
            with get_db().transaction():
                Teacher.create(
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    username=form.username.data,
                    password=hashpw(form.password.data.encode('utf-8'), gensalt())
                )
        except IntegrityError:
            flash('Username already taken')
        except DatabaseError:
            flash('An error occurred while creating a teacher')
        else:
            flash('Teacher created')
            return redirect(url_for('admin_blueprint.admin_teachers'))
    flash_errors(form)
    return render_template('new_teacher.html', form=form)


@admin_blueprint.route('/teacher_profile/<username>/', methods=['GET', 'POST'])
@admin_required
def teacher_profile(username):
    teacher = Teacher.get(Teacher.username == username)
    if request.method == 'POST':
        with get_db().transaction():
            if teacher.delete_instance(recursive=True):
                flash(teacher.username + ' deleted.')
                return redirect(url_for('admin_blueprint.admin_teachers'))
            flash('Something went wrong while trying to delete a record.')
    specs = TeacherSubject.select().where(TeacherSubject.teacher == teacher)
    return render_template('teacher_profile.html', teacher=teacher, specializations=specs)


@admin_blueprint.route('/teacher_profile/<username>/edit', methods=['GET', 'POST'])
@admin_required
def teacher_edit(username):
    teacher = Teacher.get(Teacher.username == username)
    form = TeacherEditForm(first_name=teacher.first_name, last_name=teacher.last_name)
    if form.validate_on_submit():
        with get_db().transaction():
            teacher.first_name = form.first_name.data
            teacher.last_name = form.last_name.data
            if teacher.save():
                flash(teacher.username + ' updated.')
            else:
                flash('Something went wrong.')
        return redirect(url_for('admin_blueprint.admin_teachers'))
    flash_errors(form)
    return render_template('teacher_edit.html', teacher=teacher, form=form)


@admin_blueprint.route('/add_specialization/<username>/', methods=['GET', 'POST'])
@admin_required
def add_specialization(username):
    form = AddSpecializationForm()
    if form.validate_on_submit():
        try:
            with get_db().transaction():
                spec = TeacherSubject.get_or_create(
                    teacher=Teacher.get(Teacher.username == username),
                    specialization=Subject.get(Subject.name == form.subject_select.data)
                )
        except DatabaseError:
            flash('An error occurred, try again')
        else:
            flash('Specialization added')
    subs = Subject.select()
    teacher = Teacher.get(Teacher.username == username)
    flash_errors(form)
    return render_template('add_specialization.html', teacher=teacher, subjects=subs, form=form)


@admin_blueprint.route('/add_subject/', methods=['GET', 'POST'])
@admin_required
def add_subject():
    form = AddSubjectForm()
    if form.validate_on_submit():
        try:
            with get_db().transaction():
                Subject.create(name=form.name.data)
        except DatabaseError:
            flash('An error occurred, try again.')
        else:
            flash('Subject added.')
    flash_errors(form)
    return render_template('add_subject.html', form=form)


@admin_blueprint.route('/subject/<name>/', methods=['POST'])
@admin_required
def subject_remove(name):
    subj = Subject.get(Subject.name == name)
    if subj.delete_instance(recursive=True):  # delete instance and all its' occurrences as foreign fields
        flash(subj.name + ' subject has been removed.')
    else:
        flash('Something went wrong.')
    return redirect(url_for('admin_blueprint.admin_subjects'))


@admin_blueprint.route('/subject/<name>/edit/', methods=['GET', 'POST'])
@admin_required
def subject_edit(name):
    subject = Subject.get(Subject.name == name)
    form = SubjectEditForm(name=subject.name)
    if form.validate_on_submit():
        with get_db().transaction():
            subject.name = form.name.data
            if subject.save():
                flash(subject.name + ' subject updated.')
            else:
                flash('Something went wrong.')
            flash_errors(form)
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
