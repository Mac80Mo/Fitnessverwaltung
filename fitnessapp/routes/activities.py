from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from fitnessapp import db
from fitnessapp.models.models import Activity, WeightEntry
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
        
        # Nachtrag (Höhenmeter & Herzfrequenz)
        elevation = request.form.get('elevation_gain', type=float)      # Höhenmeter
        heart_rate = request.form.get('avg_heart_rate', type=int)
        
        activity = Activity(
            user_id=session['user_id'],
            activity_type=activity_type,
            duration_min=duration,
            distance_km=distance,
            calories=calories,
            elevation_gain=elevation,
            avg_heart_rate=heart_rate
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
    
    total_elevation = sum(a.elevation_gain or 0 for a in activities)
    heart_rates = [a.avg_heart_rate for a in activities if a.avg_heart_rate]
    avg_heart_rate = round(sum(heart_rates) / len(heart_rates), 1) if heart_rates else None
    
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
        avg_per_day=avg_per_day,
        total_elevation=total_elevation,
        avg_heart_rate=avg_heart_rate
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
        activity.elevation_gain = request.form.get('elevation_gain', type=float)    # Höhenmeter
        activity.avg_heart_rate = request.form.get('avg_heart_rate', type=int)
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

@activities_bp.route('/avtivities/elevation-per-day')
def elevation_per_day_chart():
    if 'user_id' not in session:
        flash('Bitte zuerst einloggen.', 'warning')
        return redirect(url_for('auth.login'))
    
    from collections import defaultdict
    activities = Activity.query.filter_by(user_id=session['user_id']).all()
    
    grouped = defaultdict(float)
    for a in activities:
        if a.elevation_gain:
            tag = a.date.strftime('%d.%m.%Y')
            grouped[tag] += a.elevation_gain
    
    labels = list(grouped.keys())
    elevations = list(grouped.values())
    
    return render_template('activities/elevation_per_day_chart.html', labels=labels, elevations=elevations)


@activities_bp.route('/activities/heartrate-per-day')
def heartrate_per_day_chart():
    if 'user_id' not in session:
        flash('Bitte zuerst einloggen.', 'warning')
        return redirect(url_for('auth.login'))
    
    from collections import defaultdict
    activities = Activity.query.filter_by(user_id=session['user_id']).all()
    
    grouped = defaultdict(list)
    for a in activities:
        if a.avg_heart_rate:
            tag = a.date.strftime('%d.%m.%Y')
            grouped[tag].append(a.avg_heart_rate)
    
    # Durchschnitt pro Tag berechnen
    labels = []
    averages = []
    for tag, values in grouped.items():
        labels.append(tag)
        avg = round(sum(values) / len(values), 1)
        averages.append(avg)
        
    return render_template('activities/heartrate_per_day_chart.html', labels=labels, averages=averages)


##################################################################

# Route für den kombinierten Aktivitäts-Chart
@activities_bp.route('/activities/combined-chart')
def combined_chart():
    # Prüfen, ob der Nutzer eingeloggt ist
    if 'user_id' not in session:
        flash('Bitte einloggen.', 'warning')  # Hinweis für den Nutzer
        return redirect(url_for('auth.login'))  # Weiterleitung zur Login-Seite
    
    # Imports, die nur innerhalb der Funktion benötigt werden
    from collections import defaultdict
    from datetime import datetime

    # Aktuelle Nutzer-ID aus der Session holen
    user_id = session['user_id']
    
    # --- 1. Aktivitäten des Nutzers abfragen ---
    activities = Activity.query.filter_by(user_id=user_id).all()

    # defaultdict für die tägliche Aggregation (Standardwerte pro Tag):
    # Jede Tages-Zeile besteht aus: Dauer, Distanz, Höhenmeter, Kalorien, Herzfrequenz-Liste
    combined = defaultdict(lambda: {
        'duration': 0,
        'distance': 0,
        'elevation': 0,
        'calories': 0,
        'hr': []  # Liste für mehrere Pulsangaben pro Tag
    })

    # --- 2. Aktivitäten pro Tag aggregieren ---
    for a in activities:
        key = a.date.strftime('%d.%m.%Y')  # Datum als String (z. B. '16.04.2025')

        # Summierung der Werte (falls vorhanden, sonst 0)
        combined[key]['duration'] += a.duration_min or 0
        combined[key]['distance'] += a.distance_km or 0
        combined[key]['elevation'] += a.elevation_gain or 0
        combined[key]['calories'] += a.calories or 0

        # Herzfrequenz nur aufnehmen, wenn vorhanden
        if a.avg_heart_rate:
            combined[key]['hr'].append(a.avg_heart_rate)

    # --- 3. Gewichtsdaten des Nutzers abrufen ---
    weights = WeightEntry.query.filter_by(user_id=user_id).all()

    # Gewichtseinträge auf Tagesdatum abbilden (für einfache Zuordnung)
    weight_map = {
        w.date.strftime('%d.%m.%Y'): w.weight_kg
        for w in weights
    }

    # --- 4. Daten in Listen für das Chart umwandeln ---

    # Sortierte Liste aller Tages-Labels (X-Achse)
    labels = sorted(combined.keys())

    # Für jede Metrik wird eine Liste für das Chart erzeugt (geordnet nach Labels)
    durations = [combined[d]['duration'] for d in labels]
    distances = [combined[d]['distance'] for d in labels]
    elevations = [combined[d]['elevation'] for d in labels]
    calories = [combined[d]['calories'] for d in labels]

    # Durchschnittlicher Puls pro Tag, falls Einträge vorhanden – sonst `None`
    heart_rates = [
        round(sum(combined[d]['hr']) / len(combined[d]['hr']), 1)
        if combined[d]['hr'] else None
        for d in labels
    ]

    # Gewicht aus `weight_map` übernehmen – falls für das Datum nicht vorhanden: `None`
    weights = [
        weight_map[d] if d in weight_map else None
        for d in labels
    ]

    # --- 5. Übergabe der Daten an das HTML-Template (Chart.js) ---
    return render_template(
        'activities/combined_chart.html',
        labels=labels,             # X-Achse
        durations=durations,       # Zeit pro Tag
        distances=distances,       # Kilometer pro Tag
        elevations=elevations,     # Höhenmeter pro Tag
        calories=calories,         # Kalorienverbrauch pro Tag
        heart_rates=heart_rates,   # Ø Puls pro Tag
        weights=weights            # Gewicht pro Tag
    )
