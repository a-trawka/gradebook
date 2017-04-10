"""Gradebook web application, by Adrian Trawka - https://github.com/a-trawka"""
from flask import Flask, g, render_template
from wrappers import login_required, guest_status_required, teacher_required, student_required
from model import *
from admin import admin_blueprint
from view import student_login_, student_profile_, student_profile_foreign_, add_grade_, \
    teacher_login_, teacher_profile_, groups_, group_, group_foreign_, logout_

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'development'
app.config['WTF_CSRF_ENABLED'] = False
app.register_blueprint(admin_blueprint, url_prefix='/admin')

db = get_db()


def create_tables():
    """Create database tables from models, unless they already exist."""
    db.create_tables([Student, Teacher, Subject, TeacherSubject, Grade], safe=True)


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
    return student_login_()


@app.route('/student_profile/')
@student_required
def student_profile():
    return student_profile_()


@app.route('/student_profile/<username>')
@teacher_required
def student_profile_foreign(username):
    return student_profile_foreign_(username)


@app.route('/add_grade/', methods=['GET', 'POST'])
@teacher_required
def add_grade():
    return add_grade_()


@app.route('/teacher_login/', methods=['GET', 'POST'])
@guest_status_required
def teacher_login():
    return teacher_login_()


@app.route('/teacher_profile/')
@teacher_required
def teacher_profile():
    return teacher_profile_()


@app.route('/groups/')
@teacher_required
def groups():
    return groups_()


@app.route('/group/')
@student_required
def group():
    return group_()


@app.route('/group/<int:group_number>/')
@teacher_required
def group_foreign(group_number):
    return group_foreign_(group_number)


@app.route('/logout/')
@login_required
def logout():
    return logout_()


if __name__ == '__main__':
    create_tables()
    app.run(host='0.0.0.0')
