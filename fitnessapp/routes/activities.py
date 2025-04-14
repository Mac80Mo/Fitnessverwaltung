from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from fitnessapp import db
from fitnessapp.models.models import Activity

activities_bp = Blueprint('activities', __name__)

@activities_bp.route('/activities/add', methods=['GET', 'POST'])
def add_activity():
    if 'user_id' not in session:
        flash('Bitte zuerst einloggen.', 'warning')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        activity_type = request.form['activity_type']
        duration = float(request.form['duration'])
        calories = request.form.get('calories', type=float)
        
        activity = Activity(
            user_id=session['user_id'],
            activity_type=activity_type,
            duration_min=duration,
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
    return render_template('activities/activity_list.html', activities=activities)


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
