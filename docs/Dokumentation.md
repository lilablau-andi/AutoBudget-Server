# Dokumentation

## Anforderung

### Kernidee: Eine Anwendung zur Verwaltung persönlicher Finanzen mit Erfassung und Visualisierung.

### Datenquelle: Benutzereingaben.

### Mögliche Umsetzungen:

- Grundversion (Konsolenbasiert): Ein Programm, das über Befehle gesteuert wird und Daten in einer JSON- oder CSV-Datei speichert.
- Grafische Version: Eine Web- oder Desktop-Anwendung mit Formularen und grafischen Auswertungen.

### Optionale Erweiterungen & Vertiefungen:

- Budget-Funktion: Festlegen und Überwachen von monatlichen Budgets.
- CSV-Import/Export: Import von Kontoau szügen.
- Wiederkehrende Zahlungen: Automatische Verbuchung regelmäßiger Transaktionen.
- KI-Anwendung (Auto-Kategorisierung): Das System lernt aus früheren Eingaben und schlägt Kategorien für neue Ausgaben vor.

### Hilfreiche Python-Bibliotheken:

- Datenverarbeitung: pandas (zum Analysieren der Ausgaben), csv, json.
- UI: Flask (Web), Tkinter (Desktop), Kivy (Multi-Plattform-Apps).
- Datenbank: sqlite3.
- Visualisierung: Matplotlib oder Plotly.
- KI (Kategorisierung): Scikit-learn (für die Implementierung eines Textklassifikators wie Naive Bayes).

## Arbeitsprozess

### Phase 0 – Vorbereitung

Erstes Kennenlernen, Klären der Zuständigkeiten und Projektverlauf

### Phase 1 – Ideensammlung

Sammlung der möglichen Features mit Gruppenpriorisierung

[Link zur Ideensammlung](https://docs.google.com/document/d/1gkwAy95EX4EhoUTG7P---jfwCLNdW0_CehokyTYLwuA/edit?tab=t.0)

### Phase 2 - Umgebungsvorbereitung

Vorbereitung der Entwicklungsumgebung:

**Tech Stack**
| Bezeichnung | Beschreibung |
| ----------- | ----------- |
| Next.js | Frontend |
| FastAPI | FastAPI |
| Supabase Auth | Authentication für Login und Registrierung |
| Supabase Postgres | Datenbank |
| RestAPI | Kommunikation Backend Frontend |

**To-Do-Liste**
Eine To-Do Liste ist [Hier](https://lilablau-docs.notion.site/AutoBudget-2c89867aa30380a4a374de69f62412d5?source=copy_link)

### Phase 3 - UX Screening

UX-Screening in Figma. Genutzt UI-Bibliothek: shadcn/ui
Logoerstellung mit Google Gemini/Nano Banana

Demo Text
