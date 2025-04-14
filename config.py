class Config:
    # Schlüssel für Session, Login usw.
    SECRET_KEY = 'Pa$$w0rd'        # später ersetzen
    
    # Verbindung zur MySQL-Datenbank
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/fitness_db'
    
    # Keine unnötigen Änderungs-Events loggen
    SQLALCHEMY_TRACK_MODIFICATIONS = False