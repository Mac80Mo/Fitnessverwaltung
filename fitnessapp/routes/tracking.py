from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from fitnessapp import db
from fitnessapp.models.models import WeightEntry

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
    
    entries = WeightEntry.query.filter_by(user_id=session['user_id']).order_by(WeightEntry.date.desc()).all()
    return render_template('tracking/weight_list.html', entries=entries)