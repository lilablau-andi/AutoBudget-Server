# API Endpoint für die Transaktionen
# Autor: Rose Bahar

from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, and_, func, update
from datetime import date, timedelta
from typing import Optional, List
import math

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.expense import Expense
from app.schemas.expense import (
    ExpenseCreate, 
    ExpenseRead, 
    ExpenseUpdate, 
    ExpensePaginated,
    TransactionType,
    ExpenseBulkUpdate,
    ExpenseBulkDelete,
    CategorySuggestionRequest,
    CategorySuggestion
)
from app.services.import_service import ImportService
from app.services.expense_service import ExpenseService
from fastapi import File, UploadFile

# Router festlegen für spätere Funktionen. Router weist URL direkt dem Code zu
router = APIRouter()

# Registriert den POST Endpoint um Transaktionen anzulegen.
@router.post(
    "/",
    response_model=ExpenseRead, #Hier wird das Model aus /models/expense.py gezogen
    status_code=status.HTTP_201_CREATED, #Statuscode bei Erfolgreicher Erstellung
)
def create_expense( # Funktion Transaktion erstellen
    expense_in: ExpenseCreate, #Expense Schema aus /schemas/expense.py
    db: Session = Depends(get_db), #Datenbank Session -> /core/database.py
    user_id: str = Depends(get_current_user), #Welcher Nutzer legt Transaktion an?
):
    """
    Erstellt eine neue Ausgabe oder Einnahme für den aktuellen User.
    """

    expense = Expense(
        user_id=user_id,
        amount=expense_in.amount,
        type=expense_in.type,
        category_id=expense_in.category_id,
        description=expense_in.description,
        expense_date=expense_in.expense_date,
    )

    #SQAlchemy Funktionen um Transaktion zur Datenbank zu schicken
    db.add(expense) #Transaktion zum hochladen markieren
    db.commit() #Transaktion final hochladen, im Hintergrund wird SQL durchgeführt
    db.refresh(expense) #DB-Werte zurückholen. Die Datenbank schickt die neu erstellte ID zurück.

    return expense

#Registriert den GET Endpoint, um Transaktionen aus der Datenbank abzufragen
@router.get(
    "/",
    response_model=ExpensePaginated,
)
def list_expenses( #Funktion um Transaktion abzuholen
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    expense_type: Optional[TransactionType] = Query(None, alias="type"),
    category_ids: Optional[list[int]] = Query(None),
    #Entwürfe sind für den CSV-Import.
    is_draft: bool = Query(False, description="Filter: Nur Entwürfe (True) oder nur finale Buchungen (False)"), 
    sort_by: Optional[str] = Query(None, description="Sortierfeld: 'date', 'amount', 'category'"),
    sort_order: Optional[str] = Query("desc", description="Sortierreihenfolge: 'asc', 'desc'"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=5000),
):
    """
    Gibt alle Ausgaben und Einnahmen des aktuellen Users zurück (paginiert).
    Filtert nach einem Zeitraum, falls angegeben.
    Standardmäßig die letzten 30 Tage, wenn kein Zeitraum angegeben wurde.
    Sortiert nach Datum (neueste zuerst).
    """

    # ORM Statement für die Abfrage (Anstatt SQL)
    stmt = (
        select(Expense)
        .where(Expense.user_id == user_id)
        .where(Expense.is_draft == is_draft)
    )

    # Wenn kein Zeitraum angegeben ist, filtern wir standardmäßig die letzten 30 Tage
    # ABER NUR für normale Ausgaben. Entwürfe wollen wir alle sehen, um sie abzuarbeiten.
    if not is_draft and not start_date and not end_date:
        start_date = date.today() - timedelta(days=30)
    
    if start_date:
        stmt = stmt.where(Expense.expense_date >= start_date)
    
    if end_date:
        stmt = stmt.where(Expense.expense_date <= end_date)

    if category_ids:
        stmt = stmt.where(Expense.category_id.in_(category_ids))

    if expense_type:
        stmt = stmt.where(Expense.type == expense_type)

    # Gesamtzahl der Einträge berechnen (vor Pagination)
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_count = db.execute(count_stmt).scalar() or 0

    # Pagination anwenden: Das Brauchen wir damit wir nicht alle Einträge ziehen, sondern nur so viel wie wir brauchen
    # Erhöhte Performance und schnellere Ladezeit
    total_pages = math.ceil(total_count / page_size) if total_count > 0 else 0

    #Offset festlegen: Ab welcher Seite fangen wir an zu fetchen
    offset = (page - 1) * page_size

    #Wir holen hier Daten aus der Kategorie Tabelle in einer N:1 beziehung
    stmt = stmt.options(joinedload(Expense.category))
    
    # Sortierung
    if sort_by == "amount": #Sortieren nach Betrag: Wenn sort_order asc dann Absteigend sortieren, sonst andersrum
        stmt = stmt.order_by(Expense.amount.asc()) if sort_order == "asc" else stmt.order_by(Expense.amount.desc())
    elif sort_by == "category":
        # Sortieren nach Kategorie
         stmt = stmt.order_by(Expense.category_id.asc()) if sort_order == "asc" else stmt.order_by(Expense.category_id.desc())
    else:
        # Standardsortierung Datum absteigend
        if sort_order == "asc":
            stmt = stmt.order_by(Expense.expense_date.asc(), Expense.id.asc()) 
        else:
             stmt = stmt.order_by(Expense.expense_date.desc(), Expense.id.desc())

    #Offset sagt ab welcher Zeile anfangen; Limit sagt wie viele Datensätze
    stmt = stmt.offset(offset).limit(page_size)

    #Scalars macht, dass wir eine Liste von Objekten bekommen, mit der wir vernünftig arbeiten können.
    expenses = db.execute(stmt).scalars().all()

    return {
        "items": expenses,
        "meta": {
            "total_count": total_count,
            "total_pages": total_pages,
            "page": page,
            "page_size": page_size
        }
    }


#Registriert den PUT Endpoint, um ALLE Transaktionen zu aktualisieren
@router.put(
    "/{expense_id}",
    response_model=ExpenseRead,
)
def update_expense(
    expense_id: int,
    expense_in: ExpenseCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Überschreibt eine bestehende Ausgabe/Einnahme des aktuellen Users (Full Update).
    """

    #Transaktion wird erstmal abgeholt
    expense = db.get(Expense, expense_id)

    #Wenn für die angegebene ID keine Transaktion gefunden wird, dann Fehler rausschmeissen
    if not expense or expense.user_id != user_id:
        raise HTTPException(
            status_code=404,
            detail="Expense not found",
        )

    # Bei PUT überschreiben wir ALLE Felder
    expense.amount = expense_in.amount
    expense.type = expense_in.type
    expense.category_id = expense_in.category_id
    expense.description = expense_in.description
    expense.expense_date = expense_in.expense_date

    db.commit()
    db.refresh(expense)

    return expense

#Registriert den PATCH Endpoint, um einzelne Felder in einer Transaktion zu aktualiseren
@router.patch(
    "/{expense_id}",
    response_model=ExpenseRead,
)
def patch_expense(
    expense_id: int,
    expense_in: ExpenseUpdate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Aktualisiert eine bestehende Ausgabe/Einnahme des aktuellen Users (Teil-Update).
    Nur die übergebenen Felder werden geändert.
    """

    expense = db.get(Expense, expense_id)

    if not expense or expense.user_id != user_id:
        raise HTTPException(
            status_code=404,
            detail="Expense not found",
        )

    # Nur Felder aktualisieren, die explizit im angegeben wurden
    # Exclude_unset=True erzeugt den PATCH Effekt, anstatt wie PUT zu aggieren
    update_data = expense_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(expense, key, value)

    db.commit() 
    db.refresh(expense)

    return expense
    
#Registriert den PATCH Endpoint für Mehrfachänderungen
@router.patch(
    "/bulk",
    status_code=status.HTTP_200_OK,
)
def bulk_update_expenses(
    bulk_in: ExpenseBulkUpdate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Aktualisiert mehrere Ausgaben gleichzeitig (Teil-Update).
    """
    updated_count = ExpenseService.bulk_update(
        db=db,
        user_id=user_id,
        ids=bulk_in.ids,
        data=bulk_in.data,
    )
    
    return {"message": f"{updated_count} Ausgaben erfolgreich aktualisiert."}
    
#Registriert den DELETE Endpoint um mehrere Transaktionen zu löschen
@router.delete(
    "/bulk",
    status_code=status.HTTP_200_OK,
)
def bulk_delete_expenses(
    bulk_in: ExpenseBulkDelete,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Löscht mehrere Ausgaben gleichzeitig.
    """
    deleted_count = ExpenseService.bulk_delete(
        db=db,
        user_id=user_id,
        ids=bulk_in.ids,
    )

    return {"message": f"{deleted_count} Ausgaben erfolgreich gelöscht."}

# Registriert den POST Request um Kategorien beim CSV-Import vorzuschlagen.
# Warum ist das ein POST Request? GET-Requests übergeben 
# Daten normalerweise in der URL (Query Parameter). 
# URLs haben jedoch eine begrenzte Länge (oft ca. 2000 Zeichen). 
# Wenn man eine CSV mit 100 Zeilen importiert, würden die Beschreibungen 
# diese Grenze sprengen.
@router.post(
    "/suggest-categories",
    response_model=List[CategorySuggestion],
)
def suggest_categories(
    request_data: List[CategorySuggestionRequest],
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Schlägt Kategorien für eine Liste von Beschreibungen vor.
    Nutzt historische Daten des Users für die Zuordnung.
    """
    suggestions = ExpenseService.suggest_categories(
        db=db,
        user_id=user_id,
        requests=request_data
    )
    return suggestions

# Registriert den DELETE Endpoint um Transaktionen zu löschen
@router.delete(
    "/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Löscht eine Ausgabe/Einnahme des aktuellen Users.
    """

    expense = db.get(Expense, expense_id)

    if not expense or expense.user_id != user_id:
        raise HTTPException(
            status_code=404,
            detail="Expense not found",
        )

    db.delete(expense)
    db.commit()

    return None #Nichts wird zurückgegeben, weil Transaktion weg ist

# Registriert den POST Request um Dateien hochzuladen. 
# Die Transaktionen in der Datei werden als Entwurf in der Datenbank gespeichert.
@router.post(
    "/import/upload",
    status_code=status.HTTP_201_CREATED,
)
def upload_import(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Liest eine CSV-Datei ein und speichert die Transaktionen als ENTWÜRFE (is_draft=True) in die DB.
    Gibt die Anzahl der erstellten Entwürfe zurück.
    """
    content = file.file.read()
    result = ImportService.parse_csv(content) #Hier wird der ImportService genutzt /services/import_service.py
    
    #Transaktionen und Fehler aus dem Service abholen und in Liste speichern
    transactions = result.get("transactions", [])
    errors = result.get("errors", [])
    
    #Pro Transaktion in o.g. Liste ein Expense Objekt erstellen und in neuer Liste speichern.
    new_expenses = []
    for trans in transactions:
        expense = Expense(
            user_id=user_id,
            amount=trans.amount,
            type=trans.type,
            category_id=trans.category_id,
            description=trans.description,
            expense_date=trans.expense_date,
            is_draft=True
        )
        new_expenses.append(expense)

    #Wenn es eine neue Liste gibt und Transaktionen angelegt wurden, dann in die Datenbank einfügen
    if new_expenses:
        db.add_all(new_expenses)
        db.commit()

    #Anzahl der Entwürfe und Fehler zurückgeben.
    return {
        "message": f"{len(new_expenses)} Entwürfe erstellt.",
        "count": len(new_expenses),
        "errors": errors
    }

#Erstellt den POST Request um Entwürfe im CSV-Import zu speichern.
@router.post(
    "/import/commit",
    status_code=status.HTTP_200_OK,
)
def commit_import(
    request: ExpenseBulkDelete, #Wir Reusen hier das Schema vom BulkDelete, weil es das gleiche ist.
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Finalisiert die angegebenen Entwürfe (setzt is_draft=False).
    """
    stmt = (
        update(Expense)
        .where(Expense.id.in_(request.ids))
        .where(Expense.user_id == user_id)
        .where(Expense.is_draft == True)
        .values(is_draft=False)
    )
    
    result = db.execute(stmt)
    db.commit()
    
    #Abfrage, wie viele Zeilen haben wir erfolgreich hochgeladen und als return zurückgeben
    count = getattr(result, "rowcount", 0)
    return {"message": f"{count} Transaktionen finalisiert."}

# Registrierung des POST Requests für die Automatische Kategorisierung bei dem CSV-Import
@router.post(
    "/drafts/auto-categorize",
    status_code=status.HTTP_200_OK,
)
def auto_categorize_drafts(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Kategorisiert alle vorhandenen Entwürfe des Users automatisch.
    """
    # 1. Alle Entwürfe laden, die auf Entwurfstatus sind
    drafts = db.scalars(
        select(Expense)
        .where(Expense.user_id == user_id)
        .where(Expense.is_draft == True)
    ).all()
    
    #Wenn es keine Entwürfe gibt, dann wird die Funktion beendet
    if not drafts:
        return {"message": "Keine Entwürfe zum Kategorisieren gefunden."}

    # 2. Für alle Entwürfe: wenn es eine Description gibt, erstelle neues Objekt nach Schema
    suggestion_requests = [
        CategorySuggestionRequest(description=d.description, type=d.type) 
        for d in drafts if d.description
    ]
    
    # Wenn es keine Beschreibungen gibt, kann auch nicht automatisch zugeordnet werden also return
    if not suggestion_requests:
         return {"message": "Keine Entwürfe mit Beschreibung gefunden."}

    # 3. Vorschläge aus dem expense_service holen
    suggestions = ExpenseService.suggest_categories(db, user_id, suggestion_requests)
    
    # 4. Vorschläge anwenden
    # Hier nehmen wir einfach an, dass wir über description matchen.
    
    updates_count = 0
    
    #Suggestions wurde nur für Entwürfe mit Beschreibung erstellt. 
    # Aber die Reihenfolge muss identisch bleiben. Dafür sorgt die funktion.
    drafts_with_desc = [d for d in drafts if d.description]
        
    # Für jeden Vorschlag update Count zählen   
    for draft, sugg in zip(drafts_with_desc, suggestions):
        if sugg.get("confidence", 0) > 0.6 and sugg.get("suggested_category_id"):
            draft.category_id = sugg["suggested_category_id"]
            updates_count += 1
            
    db.commit()

    # Update Count zurückgeben.
    return {"message": f"{updates_count} Entwürfe automatisch kategorisiert."}