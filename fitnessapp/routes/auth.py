from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from fitnessapp import db
from fitnessapp.utils.decorators import login_required
from fitnessapp.models.models import User, WeightEntry, Activity
from fitnessapp.utils.stats import sum_attr, calc_change
from fitnessapp.utils.dates import get_month_ranges
from fitnessapp.utils.session_helpers import get_logged_in_user
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
        weight = float(request.form['weight'])
        
        # Passwort sicher hashen
        hashed_password = generate_password_hash(password)
        
        # Neuen Nutzer erstellen und speichern
        new_user = User(name = name, email = email, password = hashed_password, height_cm = height, age = age)
        db.session.add(new_user)
        db.session.commit()
        
        # Erstes Gewicht speichern
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
        
        user = get_logged_in_user()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login erfolgreich!', 'success')
            return redirect(url_for('auth.dashboard'))
        else:
            flash('Falsche E-Mail oder Passwort!', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/dashboard')
@login_required
def dashboard():
    from datetime import datetime
    user = get_logged_in_user()

    # Letztes Gewicht und BMI berechnen
    weights = sorted(user.weights, key=lambda e: e.date)
    last_weight = weights[-1].weight_kg if weights else None
    height_m = user.height_cm / 100
    bmi = round(last_weight / (height_m ** 2), 2) if last_weight else None

    # Aktivitäten heute (Datum vergleichen) !! Daraus könnten wir eine Klasse machen... !!
    today = datetime.today().date()
    todays_activities = [a for a in user.activities if a.date.date() == today]
    duration_today = sum(a.duration_min or 0 for a in todays_activities)
    calories_today = sum(a.calories or 0 for a in todays_activities)
    distance_today = sum(a.distance_km or 0 for a in todays_activities)
    elevation_today = sum(a.elevation_gain or 0 for a in todays_activities)
    hr_today = [a.avg_heart_rate for a in todays_activities if a.avg_heart_rate]
    avg_hr_today = round(sum(hr_today) / len(hr_today), 1) if hr_today else None

    # Alle Aktivitäten
    all_activities = user.activities
    
    ## Fortschrittsdaten
    from datetime import timedelta
    
    ## Vergleichsteiträume
    one_week_ago = today - timedelta(days=7)
    two_weeks_ago = today - timedelta(days=14)
    
    last_month, end_last_month = get_month_ranges(today)
    first_day_this_month = today.replace(day=1)
    
    ## Aktivitäten nach Zeiträumen filtern
    activities_this_week = [a for a in all_activities if one_week_ago <= a.date.date() <= today]
    activities_prev_week = [a for a in all_activities if two_weeks_ago <= a.date.date() < one_week_ago]

    activities_this_month = [a for a in all_activities if first_day_this_month <= a.date.date() <= today]
    activities_prev_month = [a for a in all_activities if last_month <= a.date.date() <= end_last_month]
    
    ## Summen berechnen   
    dur_this_week = sum_attr(activities_this_week, 'duration_min')
    dur_prev_week = sum_attr(activities_prev_week, 'duration_min')
    
    cal_this_week = sum_attr(activities_this_week, 'calories')
    cal_prev_week = sum_attr(activities_prev_week, 'calories')
    
    km_this_week = sum_attr(activities_this_week, 'distance_km')
    km_prev_week = sum_attr(activities_prev_week, 'distance_km')
    
    elev_this_week = sum_attr(activities_this_week, 'elevation_gain')
    elev_prev_week = sum_attr(activities_prev_week, 'elevation_gain')
    
    dur_this_month = sum_attr(activities_this_month, 'duration_min')
    dur_prev_month = sum_attr(activities_prev_month, 'duration_min')
    
    cal_this_month = sum_attr(activities_this_month, 'calories')
    cal_prev_month = sum_attr(activities_prev_month, "calories")
    
    km_this_month = sum_attr(activities_this_month, 'distance_km')
    km_prev_month = sum_attr(activities_prev_month, 'distance_km')
    
    elev_this_month = sum_attr(activities_this_month, 'elevation_gain')
    elev_prev_month = sum_attr(activities_prev_month, 'elevation_gain')
    
    
    
    ## Prozentuale Änderung berechnen   
    change_dur_week = calc_change(dur_this_week, dur_prev_week)
    change_cal_week = calc_change(cal_this_week, cal_prev_week)
    change_km_week = calc_change(km_this_week, km_prev_week)
    change_elev_week = calc_change(elev_this_week, elev_prev_week)
    change_dur_month = calc_change(dur_this_month, dur_prev_month)
    change_cal_month = calc_change(cal_this_month, cal_prev_month)
    change_km_month = calc_change(km_this_month, km_prev_month)
    change_elev_month = calc_change(elev_this_month, elev_prev_month)
    

    # Gesamtstatistiken berechnen
    total_duration = sum(a.duration_min or 0 for a in all_activities)
    total_calories = sum(a.calories or 0 for a in all_activities)
    total_distance = sum(a.distance_km or 0 for a in all_activities)
    total_elevation = sum(a.elevation_gain or 0 for a in all_activities)
    
    # Aktive Tage ermitteln
    dates = [a.date.date() for a in all_activities]
    active_days = len(set(dates))
    
    # Zeitraum ermitteln für Durchschnitt pro Tag/Woche/Monat
    if dates:
        first_date = min(dates)
        last_date = max(dates)
        num_days = (last_date - first_date).days + 1
        num_weeks = max(1, num_days // 7)
        num_months = max(1, (last_date.year - first_date.year) * 12 + (last_date.month - first_date.month + 1))

        avg_per_day = round(total_duration / num_days, 1)
        avg_per_week = round(total_duration / num_weeks, 1)
        avg_per_month = round(total_duration / num_months, 1)

        # Durchschnittliche Distanz und Höhenmeter pro Woche/Monat
        avg_km_week = round(total_distance / num_weeks, 2)
        avg_km_month = round(total_distance / num_months, 2)
        avg_elev_week = round(total_elevation / num_weeks, 1)
        avg_elev_month = round(total_elevation / num_months, 1)
    else:
        avg_per_day = avg_per_week = avg_per_month = 0
        avg_km_week = avg_km_month = avg_elev_week = avg_elev_month = 0

    # Durchschnittswerte gesamt
    avg_km = round(total_distance / active_days, 2) if active_days else 0
    avg_elevation = round(total_elevation / active_days, 1) if active_days else 0
    heart_rates_all = [a.avg_heart_rate for a in all_activities if a.avg_heart_rate]
    avg_heart_rate_all = round(sum(heart_rates_all) / len(heart_rates_all), 1) if heart_rates_all else None

    return render_template(
        'auth/dashboard.html',
        user=user,
        last_weight=last_weight,
        bmi=bmi,
        duration_today=duration_today,
        calories_today=calories_today,
        distance_today=distance_today,
        elevation_today=elevation_today,
        total_duration=total_duration,
        total_calories=total_calories,
        total_distance=total_distance,
        total_elevation=total_elevation,
        active_days=active_days,
        avg_per_day=avg_per_day,
        avg_per_week=avg_per_week,
        avg_per_month=avg_per_month,
        avg_km=avg_km,
        avg_elevation=avg_elevation,
        avg_km_week=avg_km_week,             
        avg_km_month=avg_km_month,           
        avg_elev_week=avg_elev_week,         
        avg_elev_month=avg_elev_month,       
        avg_heart_rate_all=avg_heart_rate_all,
        avg_hr_today=avg_hr_today,
        change_dur_week=change_dur_week,
        change_cal_week=change_cal_week,
        change_dur_month=change_dur_month,
        change_cal_month=change_cal_month,
        change_km_week=change_km_week,
        change_km_month=change_km_month,
        change_elev_week=change_elev_week,
        change_elev_month=change_elev_month
    )

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




