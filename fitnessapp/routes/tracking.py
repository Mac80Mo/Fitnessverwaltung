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

@tracking_bp.route('/weight/edit/<int:id>', methods=['GET', 'POST'])
def edit_weight(id):
    if 'user_id' not in session:
        flash('Bitte zuerst einloggen.', 'warning')
        return redirect(url_for('auth.login'))
    
    entry = WeightEntry.query.get_or_404(id)
    
    # Sicherstellen, dass der Eintrag dem eingeloggten User gehört
    if entry.user_id != session['user_id']:
        flash('Zugriff verweigert.', 'danger')
        return redirect(url_for('tracking.weight_list'))
    
    if request.method == 'POST':
        try:
            weight = float(request.form['weight'])
            
            if weight <= 0:
                flash('Gewicht muss größer als 0 sein!', 'danger')
                return redirect(request.url)
            
            entry.weight_kg = float(request.form['weight'])
            db.session.commit()
            flash('Eintrag erfolgreich aktualisiert.', 'success')
            return redirect(url_for('tracking.weight_list'))
        
        except ValueError:
            flash('Ungültiger Wert.', 'danger')
    
    return render_template('tracking/edit_weight.html', entry=entry)


@tracking_bp.route('/weight/delete/<int:id>', methods=['POST'])
def delete_weight(id):
    if 'user_id' not in session:
        flash('Bitte zuerst einloggen.', 'warning')
        return redirect(url_for('auth.login'))

    entry = WeightEntry.query.get_or_404(id)
    
    # Schutz: Fremde Einträge dürfen nicht gelöscht werden
    if entry.user_id != session['user_id']:
        flash('Zugriff verweigert', 'danger')
        return redirect(url_for('tracking.weight_list'))
    
    db.session.delete(entry)
    db.session.commit()
    flash('Eintrag gelöscht.', 'info')
    return redirect(url_for('tracking.weight_list'))

