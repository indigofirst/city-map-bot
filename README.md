# City Map Bot

Ein Telegram-Bot zur Suche und Visualisierung von Städten aus einer lokalen SQLite-Datenbank. Er kann persönliche Städtesammlungen speichern und die Luftlinienentfernung zwischen zwei Städten berechnen.

## Funktionen

- Städte in SQLite suchen
- einzelne Städte auf einer Weltkarte anzeigen
- Städte pro Telegram-Benutzer speichern
- gespeicherte Städte gemeinsam visualisieren
- Luftlinienentfernung zwischen zwei Städten berechnen
- Verbindung zwischen zwei Städten auf einer Karte darstellen
- Schutz vor doppeltem Speichern derselben Stadt

## Technologien

- Python 3.10+
- pyTelegramBotAPI
- SQLite / SQL
- Matplotlib
- Cartopy
- Haversine-Formel

## Projektstruktur

```text
city-map-bot/
├── .gitignore
├── bot.py
├── config.py
├── database.db
├── logic.py
├── README.md
└── requirements.txt
```

## Installation

```bash
pip install -r requirements.txt
```

Cartopy kann je nach Umgebung zusätzliche Systemabhängigkeiten benötigen.

Telegram-Bot über BotFather erstellen und den Token in `config.py` eintragen:

```python
TOKEN = "DEIN_BOT_TOKEN"
```

Bot starten:

```bash
python bot.py
```

## Befehle

- `/start` – Bot starten
- `/help` – Hilfe anzeigen
- `/show_city <Stadt>` – Stadt auf der Karte anzeigen
- `/remember_city <Stadt>` – Stadt speichern
- `/show_my_cities` – gespeicherte Städte anzeigen
- `/distance <Stadt1> | <Stadt2>` – Luftlinienentfernung berechnen

Beispiel:

```text
/distance Zurich | Paris
```

## Technische Details

- Die geografischen Koordinaten werden lokal aus SQLite gelesen; eine Geocoding-API ist nicht erforderlich.
- Matplotlib und Cartopy erzeugen PNG-Karten aus den gespeicherten Koordinaten.
- Die Entfernung wird mit der Haversine-Formel berechnet.
- Ein `UNIQUE`-Constraint verhindert doppelte Stadtzuordnungen pro Benutzer.
- Temporäre Kartendateien werden nach dem Senden automatisch entfernt.

### Datenquelle und Lizenzen

Die geografischen Informationen (Stadtnamen, Koordinaten, Länder und ISO-Codes) in `database.db` basieren auf dem globalen Open-Data-Datensatz von **SimpleMaps**.

- **Datensatz:** SimpleMaps World Cities Database (Basic Edition) mit **47.868 Städten**.
- **Lizenz:** Freie Nutzung für kommerzielle und nicht-kommerzielle Zwecke unter der **Creative Commons Attribution 4.0 International License (CC BY 4.0)**.
- **Offizielle Website:** [SimpleMaps World Cities](https://simplemaps.com)

## Einschränkungen

- Eine Stadt muss in der lokalen Datenbank vorhanden sein.
- Gleichnamige Städte können ohne zusätzliche Länderangabe nicht immer eindeutig unterschieden werden.
- Die berechnete Distanz ist die Luftlinie und keine Fahr- oder Reiseroute.

## Sicherheit

Ein echter Telegram-Bot-Token gehört nicht in ein öffentliches Repository. Die veröffentlichte Datenbank sollte keine personenbezogenen Telegram-Benutzerdaten enthalten.
