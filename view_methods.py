from forms import StudentLoginForm, AddGradeForm, TeacherLoginForm
from forms import flash_errors
from model import Student, Teacher, Subject, Grade, TeacherSubject
from model import get_db
from peewee import DatabaseError
from bcrypt import hashpw
from flask import flash, render_template, redirect, session, url_for
from custom_exceptions import WrongPasswordException


db = get_db()


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


def vm_student_login():
    form = StudentLoginForm()
    if form.validate_on_submit():
        try:
            student = Student.get(username=form.username.data)
            # adequate salt is stored in the password itself
            stored_password = student.password.encode('utf-8')
            password_to_check = form.password.data.encode('utf-8')
            password = hashpw(password_to_check, stored_password)
            if password != stored_password:
                raise WrongPasswordException('Wrong password')
        except WrongPasswordException:
            flash('Wrong password')
        except Student.DoesNotExist:
            flash('Wrong username or password')
        else:
            authorize_student(student)
            return redirect(url_for('student_profile'))
    flash_errors(form)
    return render_template('student_login.html', form=form)


def vm_student_profile():
    student = get_current_user()
    subjects = Subject.select()
    grades = Grade.select().where(Grade.student == student)
    return render_template('student_profile.html', student=student, subjects=subjects, grades=grades)


def vm_student_profile_foreign(username):
    student = Student.get(Student.username == username)
    subjects = Subject.select()
    grades = Grade.select().where(Grade.student == student)
    return render_template('student_profile.html', student=student, subjects=subjects, grades=grades)


def vm_add_grade():
    form = AddGradeForm()
    if form.validate_on_submit():
        try:
            with db.transaction():
                grade = Grade.create(
                    student=Student.get(Student.username == form.student_select.data),
                    subject=Subject.get(Subject.name == form.subject_select.data),
                    teacher=get_current_user(),
                    grade=form.grade.data
                )
        except DatabaseError:
            flash('An error occurred while adding a grade')
        else:
            flash('Grade ' + str(grade.grade) + ' assigned to student ' + str(grade.student))
            return redirect(url_for('groups', group=grade.student.username))
    flash_errors(form)
    students = Student.select()
    subjects = Subject.select()
    return render_template('add_grade.html', students=students, subjects=subjects, form=form)


def vm_teacher_login():
    form = TeacherLoginForm()
    if form.validate_on_submit():
        try:
            teacher = Teacher.get(username=form.username.data)
            # adequate salt is stored in the password itself
            stored_password = teacher.password.encode('utf-8')
            password_to_check = form.password.data.encode('utf-8')
            password = hashpw(password_to_check, stored_password)
            if password != stored_password:
                raise WrongPasswordException('Wrong password')
        except WrongPasswordException:
            flash('Wrong password')
        except Teacher.DoesNotExist:
            flash('Wrong username or password')
        else:
            authorize_teacher(teacher)
            return redirect(url_for('teacher_profile'))
    flash_errors(form)
    return render_template('teacher_login.html', form=form)


def vm_teacher_profile():
    teacher = get_current_user()
    specs = TeacherSubject.select().where(TeacherSubject.teacher == teacher)
    return render_template('teacher_profile.html', teacher=teacher, specializations=specs)


def vm_groups():
    student_groups = Student.select(Student.group).distinct().order_by(Student.group.asc())
    return render_template('groups.html', student_groups=student_groups)


def vm_group():
    group_number = get_current_user().group
    students = Student.select().where(Student.group == group_number)
    return render_template('group.html', group=group_number, students=students)


def vm_group_foreign(group_number):
    students = Student.select().where(Student.group == group_number)
    return render_template('group.html', group=group_number, students=students)


def vm_logout():
    """Clears all session elements."""
    for field in session:
        session[field] = None
    return redirect(url_for('homepage'))