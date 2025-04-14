# Flask und SQLAlechemy importieren
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Konfiguration aus config.py laden
from config import Config 

# Erzeuge eine SQLAlchemy-Datenbankinstanz
db = SQLAlchemy()

# Funktion zum Erstellen der Flask-App (Factory-Funktion)
def create_app():
    # Neue Flask-App instanzieren
    app = Flask(__name__)
    
    # Konfiguration zuweisen (z.B. DB-Zugang, Secret Key)
    app.config.from_object(Config)
    
    # Datenbank an App binden
    db.init_app(app)
    
    # Blueprint für Authentifizierung importieren
    from fitnessapp.routes.auth import auth_bp
    
    # Blueprint registrieren
    # Optional: Mit Prefix z.B. '/auth' -> /auth/register
    app.register_blueprint(auth_bp)     # oder app.register_blueprint(auth_bp, url_prefix="/auth")
    
    # Tracking-Blueprint importieren und registrieren
    from fitnessapp.routes.tracking import tracking_bp
    app.register_blueprint(tracking_bp)
    
    # Activities-Blueprint importieren
    from fitnessapp.routes.activities import activities_bp
    app.register_blueprint(activities_bp)
    
    # Modelle importieren, damit diese bei create_all() erkannt werden
    import fitnessapp.models
    
    # App zurückgeben
    return app
