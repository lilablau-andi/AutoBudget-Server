# Die Services sind Dateien zur tieferen Berechnung von Daten
# In dem Analytics Service werden Transaktionen ausgewertet und an die API zurückgegeben
# Autor: Bastian Holstein 

from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_

from app.models.expense import Expense
from app.models.category import Category

def get_grouped_category_sums(
    db: Session,
    user_id: str,
    start_date: date,
    end_date: date,
    group_by: str = "day",
    category_ids: Optional[List[int]] = None,
    transaction_type: Optional[str] = None
):
    """
    Berechnet die Summe der Ausgaben/Einnahmen pro Kategorie und Zeitraum (Tag, Woche, Monat).
    Gibt Daten zurück, die direkt für Charts verwendet werden können.
    """
    
    # Datums-Gruppierung basierend auf group_by
    if group_by == "week":
        # Anfang der Woche (Montag)
        date_trunc = func.date_trunc('week', Expense.expense_date)
    elif group_by == "month":
        # Anfang des Monats
        date_trunc = func.date_trunc('month', Expense.expense_date)
    else:
        # Standard: Tag
        date_trunc = Expense.expense_date

    # Wir schauen hier erstmal nach dem Start und Enddatum und ziehen diese Transaktionen, 
    # die im Zeitraum liegen
    stmt = (
        select(
            date_trunc.label("date"),
            func.sum(Expense.amount).label("sum"),
            Category.name.label("category_name")
        )
        .join(Category, Expense.category_id == Category.id)
        .where(
            and_(
                Expense.user_id == user_id,
                Expense.expense_date >= start_date,
                Expense.expense_date <= end_date
            )
        )
    )

    # Nach Typ filtern (Einnahmen oder Ausgaben)
    if transaction_type:
        stmt = stmt.where(Expense.type == transaction_type)
    else:
        # Standardmäßig nur Ausgaben
        stmt = stmt.where(Expense.type == "expense")

    # Optional nach Kategorien filtern
    if category_ids:
        stmt = stmt.where(Expense.category_id.in_(category_ids))

    # Gruppieren und Sortieren
    stmt = stmt.group_by(date_trunc, Category.name)
    stmt = stmt.order_by(date_trunc.asc(), Category.name.asc())

    result = db.execute(stmt).all()
    
    # Für jedes Ergebnis wird Datum in String umgewandelt und mit den 
    # Summen und Kategorie infos ausgestattet, damit wir das im Frontend
    # als Graph darstellen können.
    timeseries = {}
    for row in result:
        d_str = row.date.strftime("%Y-%m-%d") if hasattr(row.date, "strftime") else str(row.date)
        if d_str not in timeseries:
            timeseries[d_str] = {"date": row.date, "values": {}, "total": 0.0}
        
        timeseries[d_str]["values"][row.category_name] = float(row.sum)
        timeseries[d_str]["total"] += float(row.sum)

    # Sortiert nach Datum zurückgeben
    return sorted(timeseries.values(), key=lambda x: x["date"])

def get_summary_totals(
    db: Session,
    user_id: str,
    start_date: date,
    end_date: date
):
    """
    Berechnet die Gesamtsumme von Einnahmen und Ausgaben sowie die Differenz.
    """
    stmt = (
        select(
            Expense.type,
            func.sum(Expense.amount).label("total")
        )
        .where(
            and_(
                Expense.user_id == user_id,
                Expense.expense_date >= start_date,
                Expense.expense_date <= end_date
            )
        )
        .group_by(Expense.type)
    )

    results = db.execute(stmt).all()
    
    total_income = 0.0
    total_expenses = 0.0
    
    for row in results:
        if row.type == "income":
            total_income = float(row.total or 0)
        elif row.type == "expense":
            total_expenses = float(row.total or 0)
            
    return {
        "start_date": start_date,
        "end_date": end_date,
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_balance": total_income - total_expenses
    }

def get_largest_expense(
    db: Session,
    user_id: str,
    start_date: date,
    end_date: date,
    category_id: Optional[int] = None
):
    """
    Findet die höchste Ausgabe im angegebenen Zeitraum.
    """
    stmt = (
        select(Expense)
        .where(
            and_(
                Expense.user_id == user_id,
                Expense.type == "expense",
                Expense.expense_date >= start_date,
                Expense.expense_date <= end_date
            )
        )
    )

    if category_id:
        stmt = stmt.where(Expense.category_id == category_id)

    stmt = stmt.order_by(Expense.amount.desc()).limit(1)

    result = db.execute(stmt).scalar_one_or_none()
    return result
