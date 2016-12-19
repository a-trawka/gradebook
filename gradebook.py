from flask import Flask
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask import session
from flask import abort
from peewee import *

from wrappers import login_required, guest_status_required, teacher_required

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


# TeacherSubject, in other words - specializations
# One teacher may teach many subjects,
# as well as one subject may be taught by many teachers.
# Many-to-many relationship model.
class TeacherSubject(BaseModel):
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
        order_by = ('student', 'subject', )


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
        except DatabaseError:
            abort(404)
        return redirect(url_for('homepage'))

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
            abort(404)
        else:
            authorize_student(student)
            return redirect(url_for('student_profile'))
    return render_template('student_login.html')


# TODO: student's profile accessible for teachers, but not for other students
# student_profile/<username>
@app.route('/student_profile/')
@login_required
def student_profile():
    student = get_current_user()
    return render_template('student_profile.html', student=student)


# TODO: template for creating a teacher + adding TeacherSubject specialization!
@app.route('/new_teacher/')
def new_teacher():
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
            abort(404)
        else:
            authorize_teacher(teacher)
            return redirect(url_for('teacher_profile'))
    return render_template('teacher_login.html')


@app.route('/teacher_profile/')
@login_required
@teacher_required
def teacher_profile():
    teacher = get_current_user()
    # or maybe: ...select().join(Teacher)...?
    specs = TeacherSubject.select().where(TeacherSubject.teacher == teacher)
    return render_template('teacher_profile.html', teacher=teacher, specializations=specs)


@app.route('/logout/')
@login_required
def logout():
    # This funcion clears all session variables
    for field in session:
        session[field] = None
    return redirect(url_for('homepage'))

if __name__ == '__main__':
    create_tables()
    app.run()