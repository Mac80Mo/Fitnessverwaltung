

---

```markdown
# 🏋️‍♂️ Fitnessverwaltung – Sportless GmbH

Ein webbasiertes System zur persönlichen Fitnessverwaltung. Die Anwendung wurde mit **Python**, **Flask** und **MySQL** entwickelt und ermöglicht Nutzer:innen, ihre Körperdaten, sportlichen Aktivitäten und Fortschritte übersichtlich zu erfassen und auszuwerten.

---

## 🔍 Ausgangssituation

Die Mitarbeitenden der Sportless GmbH sollen in der Lage sein, ihre Fitnessdaten digital zu erfassen, visualisieren und auswerten zu können. Ziel ist eine modulare Webanwendung zur langfristigen Dokumentation von:

- Gewicht & BMI
- Aktivitäten (Laufen, Radfahren u.v.m.)
- Fortschritten im Training



## 📸 Screenshots

### Login
![Login Formular](screenshots/Screenshot-2025-04-17-084524.png)

### Dashboard
![Dashboard Statistik](screenshots/Screenshot-2025-04-17-084622.png)  
![Dashboard Tendenz](screenshots/Screenshot-2025-04-17-084644.png)  
![Diagramm Auswahl](screenshots/Screenshot-2025-04-17-084714.png)  
![Kombo Chart](screenshots/Screenshot-2025-04-17-084732.png)  
![Radfahren Und Laufen Chart](screenshots/Screenshot-2025-04-17-084754.png)

### Profil
![Profil](screenshots/Screenshot-2025-04-17-084816.png)

### Aktivitäten
![Aktivitäten](screenshots/Screenshot-2025-04-17-084837.png)

### Gewicht
![Gewicht](screenshots/Screenshot-2025-04-17-084852.png)



## ✍️ Mein Take

Ich habe mich bei der Umsetzung dieses Projekts für **Python in Verbindung mit Flask** entschieden, um meine Kenntnisse in diesen Technologien zu vertiefen. Dabei habe ich besonderen Wert auf saubere Code-Strukturen, modulare Architektur und eine einfache Benutzerführung gelegt. Das Projekt war für mich sowohl eine technische als auch konzeptionelle Lernreise.

---

## 🚀 Aktueller Stand

✅ Das System ist **funktionstüchtig** und bietet folgende Kernfunktionen:

- Benutzerverwaltung mit Login/Session
- Dashboard mit Kennzahlen & Diagrammen
- Gewichtstracking inkl. BMI und Verlauf
- Aktivitätstracking für verschiedene Sportarten
- Fortschrittsanalyse (Woche/Monat) mit visuellem Feedback
- Diagrammgalerie (Chart.js)
- Erweiterbar um weitere Module (z. B. Ernährung, API-Anbindung)

---

## ⚙️ Wichtige Funktionen

- **Dashboard** mit Tages- und Gesamtstatistik
- **Datenanalyse**: Fortschrittskarten (z. B. Kaloriensteigerung)
- **Diagramme**:
  - Gewicht & BMI Verlauf
  - Kalorien-, Distanz-, Höhenmeter-, Herzfrequenzcharts
  - Kombinations-Chart (Multidaten-Overlay)
- **Sportartspezifische Auswertungen** (z. B. nur Radfahren/Laufen)
- **Bearbeitungs- & Löschfunktionen** für Einträge
- **Responsives Layout** mit CSS und flexibler Chart-Anzeige

---

## 🔧 Setup & Installation

### Voraussetzungen

- Python 3.10+
- MySQL oder MariaDB
- Git (optional)

---

### 1. Projekt klonen

```bash
git clone https://github.com/Mac80Mo/fitnessverwaltung.git
cd fitnessverwaltung
```

---

### 2. Virtuelle Umgebung anlegen

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# oder
source venv/bin/activate  # macOS/Linux
```

---

### 3. Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

---

### 4. Datenbank vorbereiten

1. MySQL-Datenbank erstellen (z. B. `fitness_db`)
2. Zugangsdaten in der `config.py` anpassen:

```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://benutzer:passwort@localhost/fitness_db'
```

3. Tabellen initialisieren:

```bash
flask shell
>>> from fitnessapp import db
>>> db.create_all()
>>> exit()
```

---

### 5. Anwendung starten

```bash
python run.py
```

📍 Im Browser öffnen:

```
http://localhost:5000
```

---

## 🛠️ Tech-Stack

- Python 3.x
- Flask (Blueprints, Jinja2)
- MySQL / MariaDB
- Chart.js (Frontend-Visualisierung)
- HTML, CSS (responsive UI)

---

## 🧩 Nächste Schritte

- [ ] Export-/Importfunktion (CSV oder PDF)
- [ ] Nutzerrollen & Mehrbenutzerfähigkeit
- [ ] API für mobile Clients
- [ ] Integration Ernährungstracker

---

> © 2025   
> Entwickler: Marcus M.
```

---

