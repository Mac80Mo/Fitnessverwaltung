from fitnessapp.models.models import User
from flask import session

def get_logged_in_user():
    return User.query.get(session['user_id'])



