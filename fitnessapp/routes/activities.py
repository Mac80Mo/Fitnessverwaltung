from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from fitnessapp import db
from fitnessapp.models.models import Activity
from collections import defaultdict
from datetime import datetime

activities_bp = Blueprint('activities', __name__)

@activities_bp.route('/activities/add', methods=['GET', 'POST'])
def add_activity():
    if 'user_id' not in session:
        flash('Bitte zuerst einloggen.', 'warning')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        activity_type = request.form['activity_type']
        duration = float(request.form['duration'])
        distance = request.form.get('distance_km', type=float)
        calories = request.form.get('calories', type=float)
        
        activity = Activity(
            user_id=session['user_id'],
            activity_type=activity_type,
            duration_min=duration,
            distance_km=distance,
            calories=calories
        )
        
        db.session.add(activity)
        db.session.commit()
        flash('Aktivität gespeichert!', 'success')
        return redirect(url_for('activities.activity_list'))
    
    return render_template('activities/add_activity.html')


@activities_bp.route('/activities')
def activity_list():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    activities = Activity.query.filter_by(user_id=session['user_id']).order_by(Activity.date.desc()).all()
    
    # Statistik berechnen
    total_duration = sum(a.duration_min or 0 for a in activities)
    total_calories = sum(a.calories or 0 for a in activities)
    total_distance = sum(a.distance_km or 0 for a in activities)
    
    # Anzahl aktiver Tag
    days = {a.date.date() for a in activities}
    active_days = len(days)
    
    # Durchschnittszeit pro aktivem Tag
    avg_per_day = round(total_duration / active_days, 1) if active_days else 0
    
    return render_template(
        'activities/activity_list.html',
        activities=activities,
        total_duration=total_duration,
        total_calories=total_calories,
        total_distance=total_distance,
        active_days=active_days,
        avg_per_day=avg_per_day
    )


@activities_bp.route('/activities/chart')
def activity_chart():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Aktivitäten holen
    activities = Activity.query.filter_by(user_id=session['user_id']).order_by(Activity.date.asc()).all()
    
    # Gruppierung nach Datum (ohne Urzeit)
    from collections import defaultdict
    from datetime import datetime
    
    grouped = defaultdict(float)
    for a in activities:
        tag = a.date.strftime('%d.%m.%Y')
        grouped[tag] += a.duration_min or 0
    
    labels = list(grouped.keys())
    durations = list(grouped.values())
    
    return render_template('activities/activity_chart.html', labels=labels, durations=durations)


@activities_bp.route('/activities/types')
def activity_types_chart():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    activities = Activity.query.filter_by(user_id=session['user_id']).all()
    
    from collections import defaultdict
    grouped = defaultdict(float)
    
    for a in activities:
        grouped[a.activity_type] += a.duration_min or 0
    
    labels = list(grouped.keys())
    durations = list(grouped.values())
    
    return render_template('activities/activity_types_chart.html', labels=labels, durations=durations)

@activities_bp.route('/activities/calories')
def calories_chart():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    activities = Activity.query.filter_by(user_id=session['user_id']).all()
    
    from collections import defaultdict
    grouped = defaultdict(float)
    
    for a in activities:
        if a.calories:
            grouped[a.activity_type] += a.calories
    
    labels = list(grouped.keys())
    calories = list(grouped.values())
    
    return render_template('activities/calories_chart.html', labels=labels, calories=calories)


@activities_bp.route('/activities/calories-per-day')
def calories_per_day_chart():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    from collections import defaultdict
    activities = Activity.query.filter_by(user_id=session['user_id']).all()
    
    grouped = defaultdict(float)
    for a in activities:
        if a.calories:
            tag = a.date.strftime('%d.%m.%Y')
            grouped[tag] += a.calories
    
    labels = list(grouped.keys())
    calories = list(grouped.values())
    
    return render_template('activities/calories_per_day.html', labels=labels, calories=calories)


@activities_bp.route('/activities/distance-per-day')
def distance_per_day_chart():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    from collections import defaultdict
    activities = Activity.query.filter_by(user_id=session['user_id']).all()
    
    # Gruppiert nach Datum
    grouped = defaultdict(float)
    for a in activities:
        if a.distance_km:
            tag = a.date.strftime('%d.%m.%Y')
            grouped[tag] += a.distance_km
    
    labels = list(grouped.keys())
    distances = list(grouped.values())
    
    return render_template('activities/distance_per_day.html', labels=labels, distances=distances)

@activities_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_activity(id):
    if 'user_id' not in session:
        flash('Bitte einloggen.', 'warning')
        return redirect(url_for('auth.login'))
    
    activity = Activity.query.get_or_404(id)
    
    if request.method == 'POST':
        activity.activity_type = request.form['activity_type']
        activity.duration_min = float(request.form['duration_min'])
        activity.calories = float(request.form['calories']) if request.form['calories'] else None
        activity.distance_km = float(request.form['kilometers']) if request.form['kilometers'] else None
        db.session.commit()
        flash('Aktivität aktualisiert.', 'success')
        return redirect(url_for('activities.activity_list'))
    
    return render_template('activities/edit_activity.html', activity=activity)


@activities_bp.route('/delete/<int:id>', methods=['POST'])
def delete_activity(id):
    if 'user_id' not in session:
        flash('Bitte einloggen.', 'warning')
        return redirect(url_for('auth.login'))
    
    activity = Activity.query.get_or_404(id)
    db.session.delete(activity)
    db.session.commit()
    flash('Aktivität gelöscht.', 'info')
    return redirect(url_for('activities.activity_list'))

