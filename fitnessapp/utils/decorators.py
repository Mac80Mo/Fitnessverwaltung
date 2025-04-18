from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if 'user_id' not in session:
            flash('Bitte zuerst einloggen', 'warning')
            return redirect(url_for('auth.login'))
        return view_func(*args, **kwargs)
    return wrapped_view