from flask import Flask
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask import session
from flask import flash
from peewee import *
from wrappers import login_required, guest_status_required, teacher_required, student_required, admin_required
from db_model import *

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'development'

db = get_db()

def create_tables():
    """Create database tables from models, unless they already exist."""
    db.connect()
    db.create_tables([Student, Teacher, Subject, TeacherSubject, Grade], safe=True)


def authorize_student(student):
    """Enter session as a student."""
    session['logged_in'] = True
    session['user_id'] = student.id
    session['username'] = student.username
    session['type'] = 'S'


def authorize_teacher(teacher):
    """Enter session as a teacher."""
    session['logged_in'] = True
    session['user_id'] = teacher.id
    session['username'] = teacher.username
    session['type'] = 'T'


def authorize_admin():
    session['logged_in'] = True
    session['type'] = 'X'


def get_current_user():
    """Returns an object of Student or Teacher class, whose credentials are currently saved in session."""
    if session['logged_in']:
        if session['type'] == 'S':
            return Student.get(Student.username == session['username'])
        else:
            return Teacher.get(Teacher.username == session['username'])


@app.before_request
def before_request():
    g.db = db
    db.connect()


@app.after_request
def after_request(response):
    g.db.close()
    return response


@app.route('/')
def homepage():
    return render_template('homepage.html')


# TODO: make accessible for admin only
# TODO: password encryption
@app.route('/new_student/', methods=(['GET', 'POST']))
@teacher_required
def new_student():
    if request.method == 'POST' and request.form['username']:
        try:
            with db.transaction():
                student = Student.create(
                    first_name=request.form['first_name'],
                    last_name=request.form['last_name'],
                    group=request.form['group'],
                    username=request.form['username'],
                    password=request.form['password'],
                )
        except IntegrityError:
            flash('Username already taken')
        except DatabaseError:
            flash('An error occurred while creating a student')
        else:
            flash('Student added')
    return render_template('new_student.html')


@app.route('/student_login/', methods=['GET', 'POST'])
@guest_status_required
def student_login():
    if request.method == 'POST' and request.form['username']:
        try:
            student = Student.get(
                username=request.form['username'],
                password=request.form['password']
            )
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


# teacher should be able to access every student's profile information
@app.route('/student_profile/<username>/')
@teacher_required
def student_profile_foreign(username):
    student = Student.get(Student.username == username)
    subjects = Subject.select()
    grades = Grade.select().where(Grade.student == student)
    return render_template('student_profile.html', student=student, subjects=subjects, grades=grades)


# TODO: validation of the form data
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


@admin_required
@app.route('/new_teacher/', methods=['GET', 'POST'])
def new_teacher():
    if request.method == 'POST' and request.form['username']:
        try:
            with db.transaction():
                teacher = Teacher.create(
                    first_name=request.form['first_name'],
                    last_name=request.form['last_name'],
                    username=request.form['username'],
                    password=request.form['password']
                    )
        except IntegrityError:
            flash('Username already taken')
        except DatabaseError:
            flash('An error occurred while creating a teacher')
        else:
            flash('Teacher created')
    return render_template('new_teacher.html')


@app.route('/teacher_login/', methods=['GET', 'POST'])
@guest_status_required
def teacher_login():
    if request.method == 'POST' and request.form['username']:
        try:
            teacher = Teacher.get(
                username=request.form['username'],
                password=request.form['password']
            )
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


# TODO: view with all teachers + let admin edit their info
@admin_required
@app.route('/teacher_profile/<username>/')
def teacher_profile_foreign(username):
    teacher = Teacher.get(Teacher.username == username)
    specs = TeacherSubject.select().where(TeacherSubject.teacher == teacher)
    return render_template('teacher_profile.html', teacher=teacher, specializations=specs)


# TODO: improve adding specialization by admin
@admin_required
@app.route('/add_specialization/<username>/', methods=['GET', 'POST'])
def add_specialization(username):
    if request.method == 'POST':
        try:
            with db.transaction():
                spec = TeacherSubject.create(
                    teacher=Teacher.get(Teacher.username == username),
                    specialization=Subject.get(Subject.name == request.form['subject_select'])
                    )
        except DatabaseError:
            flash('An error occurred, try again')
        else:
            flash('Specialization added')
    subs = Subject.select()
    t = Teacher.get(Teacher.username == username)
    return render_template('add_specialization.html', teacher=t, subjects=subs)


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


@app.route('/admin_login/', methods=['GET', 'POST'])
@guest_status_required
def admin_login():
    if request.method == 'POST':
        if request.form['id'] == 'TEST_ADMIN' and request.form['pswd'] == 'TEST_PASSWORD':
            authorize_admin()
            return redirect(url_for('admin'))
        else:
            flash('NOPE')
    return render_template('admin_login.html')


@app.route('/admin/')
@admin_required
def admin():
    return render_template('admin.html')


@app.route('/logout/')
@login_required
def logout():
    """Clears all session elements."""
    for field in session:
        session[field] = None
    return redirect(url_for('homepage'))


if __name__ == '__main__':
    create_tables()
    app.run()
