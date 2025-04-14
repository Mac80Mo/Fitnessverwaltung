from fitnessapp import create_app

flask_app = create_app()

# Starte die Flask-Anwendung im Debug-Modus (nur für die Entwicklung)
if __name__ == '__main__':
    flask_app.run(debug=True)