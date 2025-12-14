from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.expense import Expense
from app.schemas.expense import ExpenseRead

router = APIRouter()


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
