# API Endpoint Logik für die Budgets
# Autor: Andrej Bobb

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func, and_
from datetime import date, timedelta
import calendar

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.budget import Budget
from app.models.expense import Expense
from app.schemas.budget import BudgetCreate, BudgetRead

router = APIRouter()

# GET Endpoint für die Budgets
@router.get("/", response_model=list[BudgetRead])
def get_budgets(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Listet alle Budgets auf UND berechnet den aktuellen Status (spent, remaining).
    """

    # Wir holen die Budget Tabelle und hängen die Kategorie Tabelle an. Ein Budget Eintrag, 
    # hat immer die Verknüpfung zu einer Kategorie
    budgets = db.execute(
        select(Budget)
        .where(Budget.user_id == user_id)
        .options(joinedload(Budget.category))
    ).scalars().all()

    # Wir berechnen genau, welchen Monat wir aktuell haben. 
    # Startdatum ist also immer Monatsanfang und Ende ist der letzte Tag des Monats
    today = date.today()
    start_date = date(today.year, today.month, 1)
    last_day = calendar.monthrange(today.year, today.month)[1]
    end_date = date(today.year, today.month, last_day)
    
    # Wir checken als Failsafe ob eine Kategorie zugewiesen ist
    category_ids = [b.category_id for b in budgets]
    
    if not category_ids:
        return []

    # Wir holen uns die Summe der Ausgaben (nur die Ausgaben), wo Datum in der Range ist
    # und die Kategorie passt
    stmt = (
        select(Expense.category_id, func.sum(Expense.amount))
        .where(Expense.user_id == user_id)
        .where(Expense.type == 'expense')
        .where(Expense.is_draft == False)
        .where(Expense.expense_date >= start_date)
        .where(Expense.expense_date <= end_date)
        .where(Expense.category_id.in_(category_ids))
        .group_by(Expense.category_id)
    )
    
    # Abgeholte Daten in einer Liste speichern und aus der Liste eine Map bauen, um leichter 
    # durchzuiterieren
    sums = db.execute(stmt).all()
    spent_map = {row[0]: row[1] for row in sums}

    # Wir holen uns alle Ausgaben pro Budget und speichern sie in der Liste
    # Wir rechnen aus wie viel Restbudget bleibt (absolut und prozenutell)
    results = []
    for b in budgets:
        spent = spent_map.get(b.category_id, 0.0)
        remaining = b.amount - spent
        percentage = (spent / b.amount) * 100 if b.amount > 0 else 0
        
        results.append(BudgetRead(
            id=b.id,
            category=b.category,
            amount=b.amount,
            period=b.period,
            spent=spent,
            remaining=remaining,
            percentage=percentage
        ))

    return results

# POST Endpoint um ein Budget anzulegen
@router.post("/", response_model=BudgetRead)
def create_budget(
    budget_in: BudgetCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    # Check ob bereits für die Kategorie ein Budget angelegt wurde
    existing = db.execute(
        select(Budget)
        .where(Budget.user_id == user_id)
        .where(Budget.category_id == budget_in.category_id)
    ).scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Budget für diese Kategorie existiert bereits."
        )

    new_budget = Budget(
        user_id=user_id,
        category_id=budget_in.category_id,
        amount=budget_in.amount,
        period=budget_in.period
    )
    db.add(new_budget)
    db.commit()
    db.refresh(new_budget)
    
    db.refresh(new_budget, attribute_names=["category"])
    
    return BudgetRead(
        id=new_budget.id,
        category=new_budget.category,
        amount=new_budget.amount,
        period=new_budget.period,
        spent=0.0,
        remaining=new_budget.amount,
        percentage=0.0
    )

# DELETE Request für ein Budget
@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    budget = db.execute(
        select(Budget).where(Budget.id == budget_id).where(Budget.user_id == user_id)
    ).scalar_one_or_none()
    
    if not budget:
        raise HTTPException(status_code=404, detail="Budget nicht gefunden")
        
    db.delete(budget)
    db.commit()