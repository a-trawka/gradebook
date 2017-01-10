from functools import wraps
from flask import session, redirect, url_for


def login_required(f):
    """Wrapper for methods accessible only by logged in users"""
    @wraps(f)
    def func(*args, **kwargs):
        if session.get('logged_in'):
            return f(*args, **kwargs)
        return redirect(url_for('student_login'))
    return func


def guest_status_required(f):
    """Wrapper for methods NOT accessible by logged in users"""
    @wraps(f)
    def func(*args, **kwargs):
        if session.get('logged_in'):
            return redirect(url_for('homepage'))
        return f(*args, **kwargs)
    return func


def teacher_required(f):
    """Wrapper for methods accessible only by teachers"""
    @wraps(f)
    def func(*args, **kwargs):
        if session.get('type') == 'T':
            return f(*args, **kwargs)
        return redirect(url_for('homepage'))
    return func


def student_required(f):
    """Wrapper for methods accessible only by students"""
    @wraps(f)
    def func(*args, **kwargs):
        if session.get('type') == 'S':
            return f(*args, **kwargs)
        return redirect(url_for('homepage'))
    return func


def admin_required(f):
    """Wrapper for methods accessible only by admin"""
    @wraps(f)
    def func(*args, **kwargs):
        if session.get('type') == 'X':
            return f(*args, **kwargs)
        return redirect(url_for('homepage'))
    return func
