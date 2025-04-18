from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from fitnessapp import db
from fitnessapp.models.models import Activity, WeightEntry
from collections import defaultdict
from datetime import datetime
from fitnessapp.utils.decorators import login_required
from fitnessapp.utils.db_helpers import get_user_activities, get_user_activities_by_type

activities_bp = Blueprint('activities', __name__)

@activities_bp.route('/activities/add', methods=['GET', 'POST'])
@login_required
def add_activity():    
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
@login_required
def activity_list():   
    activities = get_user_activities(session['user_id'])
    
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
@login_required
def activity_chart():   
    # Aktivitäten holen
    activities = get_user_activities(session['user_id'])
    
    # Gruppierung nach Datum (ohne Urzeit)   
    grouped = defaultdict(float)
    for a in activities:
        tag = a.date.strftime('%d.%m.%Y')
        grouped[tag] += a.duration_min or 0
    
    labels = list(grouped.keys())
    durations = list(grouped.values())
    
    return render_template('activities/activity_chart.html', labels=labels, durations=durations)


@activities_bp.route('/activities/types')
@login_required
def activity_types_chart():
    activities = get_user_activities(session['user_id'])
    
    grouped = defaultdict(float)
    
    for a in activities:
        grouped[a.activity_type] += a.duration_min or 0
    
    labels = list(grouped.keys())
    durations = list(grouped.values())
    
    return render_template('activities/activity_types_chart.html', labels=labels, durations=durations)

@activities_bp.route('/activities/calories')
@login_required
def calories_chart():   
    activities = get_user_activities(session['user_id'])
    
    grouped = defaultdict(float)
    
    for a in activities:
        if a.calories:
            grouped[a.activity_type] += a.calories
    
    labels = list(grouped.keys())
    calories = list(grouped.values())
    
    return render_template('activities/calories_chart.html', labels=labels, calories=calories)


@activities_bp.route('/activities/calories-per-day')
@login_required
def calories_per_day_chart():   
    activities = get_user_activities(session['user_id'])
    
    grouped = defaultdict(float)
    for a in activities:
        if a.calories:
            tag = a.date.strftime('%d.%m.%Y')
            grouped[tag] += a.calories
    
    labels = list(grouped.keys())
    calories = list(grouped.values())
    
    return render_template('activities/calories_per_day.html', labels=labels, calories=calories)


@activities_bp.route('/activities/distance-per-day')
@login_required
def distance_per_day_chart():
    activities = get_user_activities(session['user_id'])
    
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
@login_required
def edit_activity(id):   
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
@login_required
def delete_activity(id):   
    activity = Activity.query.get_or_404(id)
    db.session.delete(activity)
    db.session.commit()
    flash('Aktivität gelöscht.', 'info')
    return redirect(url_for('activities.activity_list'))

@activities_bp.route('/avtivities/elevation-per-day')
@login_required
def elevation_per_day_chart():   
    activities = get_user_activities(session['user_id'])
    
    grouped = defaultdict(float)
    for a in activities:
        if a.elevation_gain:
            tag = a.date.strftime('%d.%m.%Y')
            grouped[tag] += a.elevation_gain
    
    labels = list(grouped.keys())
    elevations = list(grouped.values())
    
    return render_template('activities/elevation_per_day_chart.html', labels=labels, elevations=elevations)


@activities_bp.route('/activities/heartrate-per-day')
@login_required
def heartrate_per_day_chart():   
    activities = get_user_activities(session['user_id'])
    
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
@login_required
def combined_chart():   
    # Aktuelle Nutzer-ID aus der Session holen
    user_id = session['user_id']
    
    # --- 1. Aktivitäten des Nutzers abfragen ---
    activities = get_user_activities(session['user_id'])

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

#####################################################################

@activities_bp.route('/activities/bike-chart')
@login_required
def bike_chart():        
    user_id = session['user_id']
    
    # Nur Radfahren-Aktivitäten filtern
    cycling_activities = get_user_activities_by_type(user_id, "Radfahren")
    
    # Gruppierung nach Tag
    data = defaultdict(lambda: {'duration': 0, 'distance': 0, 'elevation': 0, 'hr': []})
    
    for a in cycling_activities:
        key = a.date.strftime('%d.%m.%Y')
        data[key]['duration'] += a.duration_min or 0
        data[key]['distance'] += a.distance_km or 0
        data[key]['elevation'] += a.elevation_gain or 0
        if a.avg_heart_rate:
            data[key]['hr'].append(a.avg_heart_rate)
    
    # Vorbereitung der Datenreihen
    labels = sorted(data.keys())
    durations = [data[d]['duration'] for d in labels]
    distances = [data[d]['distance'] for d in labels]
    elevations = [data[d]['elevation'] for d in labels]
    heart_rates = [round(sum(data[d]['hr']) / len(data[d]['hr']), 1) if data[d]['hr'] else None for d in labels]
    
    return render_template(
        'activities/bike_chart.html',
        labels=labels,
        durations=durations,
        distances=distances,
        elevations=elevations,
        heart_rates=heart_rates
    )
    
################################################################

@activities_bp.route('/activities/run-chart')
@login_required
def run_chart():
    user_id = session['user_id']
    
    # Nur Lauf-Aktivitäten filtern
    activities = get_user_activities_by_type(user_id, "Laufen")

    grouped = defaultdict(lambda: {'duration': 0, 'distance': 0, 'elevation': 0, 'hr': []})

    for a in activities:
        date_key = a.date.strftime('%d.%m.%Y')
        grouped[date_key]['duration'] += a.duration_min or 0
        grouped[date_key]['distance'] += a.distance_km or 0
        grouped[date_key]['elevation'] += a.elevation_gain or 0
        if a.avg_heart_rate:
            grouped[date_key]['hr'].append(a.avg_heart_rate)

    # Hier: Sortiere nach echtem Datum, nicht nach alphabetisch
    labels = sorted(grouped.keys(), key=lambda d: datetime.strptime(d, '%d.%m.%Y'))

    # Entsprechend sortierte Werte extrahieren
    durations = [grouped[d]['duration'] for d in labels]
    distances = [grouped[d]['distance'] for d in labels]
    elevations = [grouped[d]['elevation'] for d in labels]
    heart_rates = [round(sum(grouped[d]['hr']) / len(grouped[d]['hr']), 1) if grouped[d]['hr'] else None for d in labels]

    print("Lauf-Daten:")
    for d in labels:
        print(f"{d} → Zeit: {grouped[d]['duration']} min, Distanz: {grouped[d]['distance']} km, Höhenmeter: {grouped[d]['elevation']}, HR: {grouped[d]['hr']}")


    return render_template(
        'activities/run_chart.html',
        labels=labels,
        durations=durations,
        distances=distances,
        elevations=elevations,
        heart_rates=heart_rates
    )


