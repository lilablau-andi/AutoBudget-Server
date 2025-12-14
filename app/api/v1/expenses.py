from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.expense import Expense
from app.schemas.expense import ExpenseCreate, ExpenseRead

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
        category=expense_in.category,
        description=expense_in.description,
        expense_date=expense_in.expense_date,
    )

    db.add(expense)
    db.commit()
    db.refresh(expense)

    return expense


@router.get(
    "/",
    response_model=list[ExpenseRead],
)
def list_expenses(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Gibt alle Ausgaben und Einnahmen des aktuellen Users zurück.
    Sortiert nach Datum (neueste zuerst).
    """

    stmt = (
        select(Expense)
        .where(Expense.user_id == user_id)
        .order_by(Expense.expense_date.desc())
    )

    expenses = db.execute(stmt).scalars().all()

    return expenses

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
    Aktualisiert eine bestehende Ausgabe/Einnahme des aktuellen Users.
    """

    expense = db.get(Expense, expense_id)

    if not expense or expense.user_id != user_id:
        raise HTTPException(
            status_code=404,
            detail="Expense not found",
        )

    # Felder aktualisieren
    expense.amount = expense_in.amount
    expense.type = expense_in.type
    expense.category = expense_in.category
    expense.description = expense_in.description
    expense.expense_date = expense_in.expense_date

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