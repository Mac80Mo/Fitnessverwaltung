from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from fitnessapp import db
from fitnessapp.utils.decorators import login_required
from fitnessapp.models.models import User, WeightEntry
from fitnessapp.utils.stats import sum_attr, calc_change
from fitnessapp.utils.dates import get_month_ranges
from fitnessapp.utils.session_helpers import get_logged_in_user
from fitnessapp.utils.dashboard_stats import calculate_dashboard_stats
from datetime import date

auth_bp = Blueprint('auth', __name__)

# Registrierung
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        height = request.form.get('height')
        age = request.form.get('age')
        weight = request.form.get('weight')
        
        # Leere Felder prüfen
        if not name or not email or not password or not height or not age or not weight:
            flash("Bitte fülle alle Pflichtfelder aus!", 'danger')
            return redirect(request.url)
        
        # Werte umwandeln und validieren
        try:
            height = float(height)
            age = int(age)
            weight = float(weight)
        except ValueError:
            flash("Ungültige Eingaben!?", 'danger')
            return redirect(request.url)

        # Passwort hashen und bei User anlegen
        hashed_password = generate_password_hash(password)
        new_user = User(name=name, email=email, password=hashed_password, height_cm=height, age=age)
        db.session.add(new_user)
        db.session.commit()

        # Gewichtseintrag
        first_weight = WeightEntry(user_id=new_user.id, weight_kg=weight)
        db.session.add(first_weight)
        db.session.commit()
        
        flash('Registrierung erfolgreich! Bitte einloggen.')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

# Login
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login erfolgreich!', 'success')
            return redirect(url_for('auth.dashboard'))
        else:
            flash('Falsche E-Mail oder Passwort!', 'danger')

    return render_template('auth/login.html')

# Dashboard
@auth_bp.route('/dashboard')
@login_required
def dashboard():
    user = get_logged_in_user()
    context = calculate_dashboard_stats(user)
    return render_template('auth/dashboard.html', **context)

# Logout
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Du wurdest ausgeloggt.', 'info')
    return redirect(url_for('auth.login'))

# Profilseite
@auth_bp.route('/profile')
@login_required
def profile():
    user = get_logged_in_user()
    weights = sorted(user.weights, key=lambda e: e.date)

    if weights:
        last_weight = weights[-1].weight_kg
        height_m = user.height_cm / 100
        bmi = round(last_weight / (height_m ** 2), 2)

        num_entries = len(weights)
        avg_weight = round(sum(w.weight_kg for w in weights) / num_entries, 1)
        min_weight = min(w.weight_kg for w in weights)
        max_weight = max(w.weight_kg for w in weights)
        start_date = weights[0].date.strftime('%d.%m.%Y')
        end_date = weights[-1].date.strftime('%d.%m.%Y')

        labels = [w.date.strftime('%d.%m.%Y') for w in weights]
        weights_data = [w.weight_kg for w in weights]
        bmis_data = [round(w.weight_kg / (height_m ** 2), 2) for w in weights]
    else:
        bmi = None
        num_entries = avg_weight = min_weight = max_weight = None
        start_date = end_date = None
        labels = weights_data = bmis_data = []

    return render_template(
        'auth/profile.html',
        user=user,
        bmi=bmi,
        num_entries=num_entries,
        current_weight=last_weight,
        avg_weight=avg_weight,
        min_weight=min_weight,
        max_weight=max_weight,
        start_date=start_date,
        end_date=end_date,
        labels=labels,
        weights_data=weights_data,
        bmis_data=bmis_data
    )

# Profil bearbeiten
@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = get_logged_in_user()

    if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']
        user.age = int(request.form['age'])
        user.height_cm = float(request.form['height_cm'])

        db.session.commit()
        flash('Profil erfolgreich aktualisiert.', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/edit_profile.html', user=user)
