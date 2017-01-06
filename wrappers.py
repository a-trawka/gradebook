from functools import wraps
from flask import session, redirect, url_for


# wrapper for methods accessible only by logged in users
def login_required(f):
    @wraps(f)
    def func(*args, **kwargs):
        if session.get('logged_in'):
            return f(*args, **kwargs)
        return redirect(url_for('student_login'))
    return func


# wrapper for methods NOT accessible by logged in users
def guest_status_required(f):
    @wraps(f)
    def func(*args, **kwargs):
        if session.get('logged_in'):
            return redirect(url_for('homepage'))
        return f(*args, **kwargs)
    return func


# wrapper for methods accessible only by teachers
def teacher_required(f):
    @wraps(f)
    def func(*args, **kwargs):
        if session.get('type') == 'T':
            return f(*args, **kwargs)
        return redirect(url_for('homepage'))
    return func


# wrapper for methods accessible only by students
def student_required(f):
    @wraps(f)
    def func(*args, **kwargs):
        if session.get('type') == 'S':
            return f(*args, **kwargs)
        return redirect(url_for('homepage'))
    return func


