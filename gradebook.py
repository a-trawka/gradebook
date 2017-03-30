"""Gradebook web application, by Adrian Trawka - https://github.com/a-trawka"""
from flask import Flask, g, render_template
from wrappers import login_required, guest_status_required, teacher_required, student_required
from model import *
from admin import admin_blueprint
from view_methods import vm_student_login, vm_student_profile, vm_student_profile_foreign, vm_add_grade, \
    vm_teacher_login, vm_teacher_profile, vm_groups, vm_group, vm_group_foreign, vm_logout

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
    return vm_student_login()


@app.route('/student_profile/')
@student_required
def student_profile():
    return vm_student_profile()


@app.route('/student_profile/<username>')
@teacher_required
def student_profile_foreign(username):
    return vm_student_profile_foreign(username)


@app.route('/add_grade/', methods=['GET', 'POST'])
@teacher_required
def add_grade():
    return vm_add_grade()


@app.route('/teacher_login/', methods=['GET', 'POST'])
@guest_status_required
def teacher_login():
    return vm_teacher_login()


@app.route('/teacher_profile/')
@teacher_required
def teacher_profile():
    return vm_teacher_profile()


@app.route('/groups/')
@teacher_required
def groups():
    return vm_groups()


@app.route('/group/')
@student_required
def group():
    return vm_group()


@app.route('/group/<int:group_number>/')
@teacher_required
def group_foreign(group_number):
    return vm_group_foreign(group_number)


@app.route('/logout/')
@login_required
def logout():
    return vm_logout()


if __name__ == '__main__':
    create_tables()
    app.run(host='0.0.0.0')
