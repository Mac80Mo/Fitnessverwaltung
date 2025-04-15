from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from fitnessapp import db
from fitnessapp.models.models import User, WeightEntry, Activity
from datetime import date

auth_bp = Blueprint('auth', __name__)

# Registrierung
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        height = float(request.form['height'])
        age = int(request.form['age'])
        
        # Passwort sicher hashen
        hashed_password = generate_password_hash(password)
        
        # Neuen Nutzer erstellen und speichern
        new_user = User(name = name, email = email, password = hashed_password, height_cm = height, age = age)
        db.session.add(new_user)
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

# Dashboard (Testseite)
@auth_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Bitte zuerst einloggen.', 'warning')
        return redirect(url_for('auth.login'))
    
    flash('Flash funktioniert!', 'success')
    
    user = User.query.get(session['user_id'])
    
    # Letztes Gewicht
    weights = sorted(user.weights, key=lambda e: e.date)
    last_weight = weights[-1].weight_kg if weights else None
    
    # BMI
    bmi = None
    if last_weight:
        height_m = user.height_cm / 100
        bmi = round(last_weight / (height_m ** 2), 2)
    
    # Aktivitäten heute
    today = date.today()
    today_activities = [
        a for a in user.activities if a.date.date() == today
    ]
    
    duration_today = sum(a.duration_min or 0 for a in today_activities)
    calories_today = sum(a.calories or 0 for a in today_activities)
    distance_today = sum(a.distance_km or 0 for a in today_activities)
    
    return render_template(
        'auth/dashboard.html', 
        user=user,
        bmi=bmi,
        last_weight=last_weight,
        duration_today=duration_today,
        calories_today=calories_today,
        distance_today=distance_today
    )

# Logout
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Du wurdest ausgeloggt.', 'info')
    return redirect(url_for('auth.login'))

# Profilseite
@auth_bp.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Bitte zuerst einloggen.', 'warning')
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['user_id'])
    weights = sorted(user.weights, key=lambda e: e.date)
    
    if weights:
        last_weight = weights[-1].weight_kg
        height_m = user.height_cm / 100
        bmi = round(last_weight / (height_m ** 2), 2)
        
        # Statistikdaten berrechnen
        num_entries = len(weights)
        avg_weight = round(sum(w.weight_kg for w in weights) / num_entries, 1)
        min_weight = min(w.weight_kg for w in weights)
        max_weight = max(w.weight_kg for w in weights)
        start_date = weights[0].date.strftime('%d.%m.%Y')
        end_date = weights[-1].date.strftime('%d.%m.%Y')
        
        # Diagrammdaten
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
    
@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        flash('Bitte zuerst einloggen.', 'warning')
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']
        user.age = int(request.form['age'])
        user.height_cm = float(request.form['height_cm'])
        
        db.session.commit()
        flash('Profil erfolgreich aktualisiert.', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/edit_profile.html', user=user)




