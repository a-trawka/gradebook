from flask import Flask
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask import session
from peewee import *

app = Flask(__name__)
app.debug = False
db = SqliteDatabase('gradebook.db')
app.secret_key = 'gjk4*d/gaDc ;34d;Q'


class BaseModel(Model):
    class Meta:
        database = db


class Subject(BaseModel):
    name = CharField()

    class Meta:
        order_by = ('name',)


class Teacher(BaseModel):
    first_name = CharField()
    last_name = CharField()
    specialization = ForeignKeyField(Subject, related_name='specializations')
    username = CharField(unique=True)
    password = CharField()


class Student(BaseModel):
    first_name = CharField()
    last_name = CharField()
    group = CharField()
    username = CharField(unique=True)
    password = CharField()


class Grades(BaseModel):
    student = ForeignKeyField(Student)
    subject = ForeignKeyField(Subject)
    teacher = ForeignKeyField(Teacher)
    grade = CharField()
    # grade_date = DateField()

    class Meta:
        # TODO: ^add related_names ++ indexes here?
        order_by = ('subject',)


def create_tables():
    db.connect()
    db.create_tables([Student, Teacher, Subject, Grades], safe=True)


def authorize_student(stud):
    session['logged_in'] = True
    session['user_id'] = stud.id
    session['username'] = stud.username


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
        except EnvironmentError:
            print('DEBUG: envir error')
        return redirect(url_for('student_login'))

    return render_template('new_student.html')


@app.route('/student_login/', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST' and request.form['username']:
        try:
            student = Student.get(
                username=request.form['username'],
                password=request.form['password']
            )
        except Student.DoesNotExist:
            # TODO: better exception catching
            print("DEBUG: student does not exist")
        else:
            authorize_student(student)
            # TODO: return redirect to some private page?
    return render_template('student_login.html')


if __name__ == '__main__':
    create_tables()
    app.run()
