from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, and_, func
from datetime import date, timedelta
from typing import Optional
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
    ImportPreview,
    BatchImportCreate
)
from app.services.import_service import ImportService
from fastapi import File, UploadFile

router = APIRouter()


@router.post(
    "/",
    response_model=ExpenseRead,
    status_code=status.HTTP_201_CREATED,
)
def create_expense(
    expense_in: ExpenseCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
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

    db.add(expense)
    db.commit()
    db.refresh(expense)

    return expense

@router.get(
    "/",
    response_model=ExpensePaginated,
)
def list_expenses(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    expense_type: Optional[TransactionType] = Query(None, alias="type"),
    category_ids: Optional[list[int]] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    """
    Gibt alle Ausgaben und Einnahmen des aktuellen Users zurück (paginiert).
    Filtert nach einem Zeitraum, falls angegeben.
    Standardmäßig die letzten 30 Tage, wenn kein Zeitraum angegeben wurde.
    Sortiert nach Datum (neueste zuerst).
    """

    # Basis-Statement für die Abfrage
    stmt = (
        select(Expense)
        .where(Expense.user_id == user_id)
    )

    # Wenn kein Zeitraum angegeben ist, filtern wir standardmäßig die letzten 30 Tage
    if not start_date and not end_date:
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

    # Pagination anwenden
    total_pages = math.ceil(total_count / page_size) if total_count > 0 else 0
    offset = (page - 1) * page_size

    stmt = stmt.options(joinedload(Expense.category))
    stmt = stmt.order_by(Expense.expense_date.desc(), Expense.id.desc())
    stmt = stmt.offset(offset).limit(page_size)

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

    expense = db.get(Expense, expense_id)

    if not expense or expense.user_id != user_id:
        raise HTTPException(
            status_code=404,
            detail="Expense not found",
        )

    # Bei PUT überschreiben wir alle Felder
    expense.amount = expense_in.amount
    expense.type = expense_in.type
    expense.category_id = expense_in.category_id
    expense.description = expense_in.description
    expense.expense_date = expense_in.expense_date

    db.commit()
    db.refresh(expense)

    return expense

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

    # Nur Felder aktualisieren, die explizit im Body gesendet wurden
    update_data = expense_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(expense, key, value)

    db.commit()
    db.refresh(expense)

    return expense

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

    return None


@router.post(
    "/import/preview",
    response_model=ImportPreview,
)
def import_preview(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user),
):
    """
    Liest eine CSV-Datei ein und gibt eine Vorschau der Transaktionen zurück.
    """
    content = file.file.read()
    result = ImportService.parse_csv(content)
    return result


@router.post(
    "/import/batch",
    status_code=status.HTTP_201_CREATED,
)
def import_batch(
    import_data: BatchImportCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Speichert mehrere Transaktionen gleichzeitig in die Datenbank.
    """
    expenses = []
    for trans in import_data.transactions:
        expense = Expense(
            user_id=user_id,
            amount=trans.amount,
            type=trans.type,
            category_id=trans.category_id,
            description=trans.description,
            expense_date=trans.expense_date,
        )
        expenses.append(expense)

    db.add_all(expenses)
    db.commit()

    return {"message": f"{len(expenses)} Transaktionen erfolgreich importiert."}