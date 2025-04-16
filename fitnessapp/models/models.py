from datetime import datetime, timezone
from fitnessapp import db

# Benutzer-Modell: enthält Basisdaten (Stammdaten der User)
class User(db.Model):
    __tablename__ = 'users'             # Tabellen-Name
    
    id = db.Column(db.Integer, primary_key=True)                    # ID
    name = db.Column(db.String(100), nullable=False)                # Vor- oder vollständiger Name
    email = db.Column(db.String(129), unique=True, nullable=False)  # Einmalige E-Mail-Adresse
    password = db.Column(db.String(200), nullable=False)            # Passwort (Hash)
    height_cm = db.Column(db.Float, nullable=False)                 # Körpergröße
    age = db.Column(db.Integer, nullable=False)                     # Alter
    
    # Beziehungen zu den Gewichtseinträgen bzw. den Aktivitäten
    weights = db.relationship('WeightEntry', backref='user', lazy=True)
    activities = db.relationship('Activity', backref='user', lazy=True)

# Gewichts-Modell
class WeightEntry(db.Model):
    __tablename__ = 'weight_entries'    # Tabellen-Name
    
    id = db.Column(db.Integer, primary_key=True)                                    # ID
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)      # Fremdschlüßel
    weight_kg = db.Column(db.Float, nullable=False)                                 # Gewicht (kg)
    date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))       # Datum (UTC-Zeitpunkt)


# Aktivitäts-Modell
class Activity(db.Model):
    __tablename__ = 'activities'        # Tabellen-Name
    
    id = db.Column(db.Integer, primary_key=True)                                    # ID
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)      # Fremdschlüßel (z. User)
    activity_type = db.Column(db.String(100), nullable=False)                       # z.B. Laufen, Radfahren, etc...
    duration_min = db.Column(db.Float)                                              # Dauer in Minuten
    calories = db.Column(db.Float)                                                  # Kalorienverbr. (Optional)
    distance_km = db.Column(db.Float)                                               # Kilometer bzw. Distanz
    date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))       # Datum d. Aktivität
    elevation_gain = db.Column(db.Float)                                            # Höhenmeter
    avg_heart_rate = db.Column(db.Integer)                                          # ds. Herzfrequenz
