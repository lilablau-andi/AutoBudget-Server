from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_

from app.models.expense import Expense
from app.models.category import Category

def get_category_daily_sums(
    db: Session,
    user_id: str,
    start_date: date,
    end_date: date,
    category_ids: Optional[List[int]] = None
):
    """
    Berechnet die Summe der Ausgaben pro Kategorie und Tag im angegebenen Zeitraum.
    """
    
    # Query aufbauen
    stmt = (
        select(
            Expense.expense_date.label("date"),
            func.sum(Expense.amount).label("sum"),
            Category.name.label("category_name")
        )
        .join(Category, Expense.category_id == Category.id)
        .where(
            and_(
                Expense.user_id == user_id,
                Expense.type == "expense",
                Expense.expense_date >= start_date,
                Expense.expense_date <= end_date
            )
        )
    )

    # Optional nach Kategorien filtern
    if category_ids:
        stmt = stmt.where(Expense.category_id.in_(category_ids))

    # Gruppieren und Sortieren
    stmt = stmt.group_by(Expense.expense_date, Category.name)
    stmt = stmt.order_by(Expense.expense_date.asc(), Category.name.asc())

    # Ausführen
    result = db.execute(stmt).all()
    
    return result
