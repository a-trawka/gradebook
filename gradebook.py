from flask import Flask
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask import session
from flask import flash
from peewee import *

from wrappers import login_required, guest_status_required, teacher_required, student_required

app = Flask(__name__)
app.debug = True
app.secret_key = 'gjk4*d/gaDc ;34d;Q'

db = SqliteDatabase('gradebook.db')


class BaseModel(Model):
    class Meta:
        database = db


class Subject(BaseModel):
    name = CharField()


class Teacher(BaseModel):
    first_name = CharField()
    last_name = CharField()
    username = CharField(unique=True)
    password = CharField()


class TeacherSubject(BaseModel):
    """TeacherSubject, in other words - specializations
    One teacher may teach many subjects,
    as well as one subject may be taught by many teachers.
    Many-to-many relationship model."""
    teacher = ForeignKeyField(Teacher, related_name='teachers')
    specialization = ForeignKeyField(Subject, related_name='specializations')


class Student(BaseModel):
    first_name = CharField()
    last_name = CharField()
    group = CharField()
    username = CharField(unique=True)
    password = CharField()


class Grade(BaseModel):
    student = ForeignKeyField(Student)
    subject = ForeignKeyField(Subject)
    teacher = ForeignKeyField(Teacher)
    grade = CharField()

    class Meta:
        order_by = ('student', 'subject',)


def create_tables():
    db.connect()
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
            flash('Username already taken.')
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


@app.route('/add_grade/', methods=['GET', 'POST'])
@teacher_required
def add_grade():
    if request.method == 'POST':
        # TODO: validation of grade form
        if request.form['student_select'] == 'default' or request.form['subject_select'] == 'default' or request.form['grade_select'] == 'default':
            flash('Select valid options')
            return redirect(url_for('homepage.html'))
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


# TODO: admin user
# TODO: adding TeacherSubject specialization!
# TODO: @admin_required wrapper
@app.route('/new_teacher/', methods=['GET', 'POST'])
def new_teacher():
    if request.method == 'POST' and request.form['username']:
        try:
            teacher = Teacher.create(
                first_name=request.form['first_name'],
                last_name=request.form['last_name'],
                username=request.form['username'],
                password=request.form['password']
                )
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
    # or maybe: ...select().join(Teacher)...?
    specs = TeacherSubject.select().where(TeacherSubject.teacher == teacher)
    return render_template('teacher_profile.html', teacher=teacher, specializations=specs)

# TODO: @admin_required
@app.route('/add_specialization/', methods=['GET', 'POST'])
def add_specialization():
    return render_template('add_specialization.html')

@app.route('/groups/')
@login_required
def groups():
    distinct_groups = Student.select(Student.group).order_by(Student.group.asc())
    return render_template('groups.html', groups=distinct_groups)


@app.route('/group/<int:group>/')
@login_required
def group(group):
    students = Student.select().where(Student.group == group)
    return render_template('group.html', group=group, students=students)


@app.route('/logout/')
@login_required
def logout():
    """Clears all session variables"""
    for field in session:
        session[field] = None
    return redirect(url_for('homepage'))


if __name__ == '__main__':
    create_tables()
    app.run()
