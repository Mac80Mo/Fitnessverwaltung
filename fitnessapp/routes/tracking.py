from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from fitnessapp import db
from fitnessapp.models.models import WeightEntry, User

tracking_bp = Blueprint('tracking', __name__)

@tracking_bp.route('/weight/add', methods=['GET', 'POST'])
def add_weight():
    if 'user_id' not in session:
        flash('Bitte zuerst einloggen.', 'warning')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        weight = float(request.form['weight'])
        new_entry = WeightEntry(user_id=session['user_id'], weight_kg=weight)
        db.session.add(new_entry)
        db.session.commit()
        return redirect(url_for('tracking.weight_list'))
    
    return render_template('tracking/add_weight.html')

@tracking_bp.route('/weight/list')
def weight_list():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    entries = WeightEntry.query.filter_by(user_id=user_id).order_by(WeightEntry.date.desc()).all()
    
    # BMI berechnen, wenn Gewicht vorhanden ist
    if entries:
        aktuelles_gewicht = entries[0].weight_kg
        größe_m = user.height_cm / 100
        bmi = aktuelles_gewicht / (größe_m ** 2)
        bmi = round(bmi, 2)
    else:
        bmi = None
    
    return render_template('tracking/weight_list.html', entries=entries, bmi=bmi)

@tracking_bp.route('/weight/chart')
def weight_chart():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    entries = WeightEntry.query.filter_by(user_id=user_id).order_by(WeightEntry.date.asc()).all()
    
    # Daten für das Diagramm vorbereiten
    labels = [entry.date.strftime('%d.%m.%Y') for entry in entries]
    weights = [entry.weight_kg for entry in entries]
    
    #BMI für jeden Eintrag berechnen
    height_m = user.height_cm / 100
    bmis = [round(weight / (height_m ** 2), 2) for weight in weights]
    
    return render_template('tracking/weight_chart.html', labels=labels, weights=weights, bmis=bmis)