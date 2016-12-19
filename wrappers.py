from functools import wraps
from flask import session, redirect, url_for


def login_required(f):
    @wraps(f)
    def func(*args, **kwargs):
        if session.get('logged_in'):
            return f(*args, **kwargs)
        return redirect(url_for('student_login'))
    return func


# wrapper for methods which cannot be accessed by a user who is already signed in (login, sign up)
def guest_status_required(f):
    @wraps(f)
    def func(*args, **kwargs):
        if session.get('logged_in'):
            return redirect(url_for('homepage'))
        return f(*args, **kwargs)
    return func


