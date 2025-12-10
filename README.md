# AutoBudget

AutoBudget ist ein Python-Tool, das Ihnen dabei hilft, Ihre Finanzen zu verwalten.

## Anforderungen

- **Python 3.12** oder höher
- PostgreSQL-Datenbank

## Installation

1. **Repository klonen:**

   ```bash
   git clone <repository-url>
   cd AutoBudget/backend
   ```

2. **Virtuelle Umgebung erstellen:**

   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate  # Auf Windows: .venv\Scripts\activate
   ```

3. **Abhängigkeiten installieren:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Umgebungsvariablen konfigurieren:**
   Erstelle eine `.env` Datei im Backend-Verzeichnis mit den notwendigen Konfigurationen.

## Nutzung

Den Development-Server starten:

```bash
uvicorn app.main:app --reload
```

Die API ist dann unter `http://localhost:8000` erreichbar.
API-Dokumentation: `http://localhost:8000/docs`

## Bibliotheken

- **fastapi** – Web-Framework
- **uvicorn** – ASGI-Server
- **pydantic** – Datenvalidierung
- **sqlalchemy** – ORM
- **psycopg** – PostgreSQL-Adapter
