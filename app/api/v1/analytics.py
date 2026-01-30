# API Endpoint Logik für Analysedaten, z.B. Transaktionensummen von Zeiträumen
# Autor: Bastian Holstein

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.analytics import SummaryTotals, LargestExpense, GroupBy, TimeseriesPoint
from app.services import analytics_service

router = APIRouter()


# GET Endpoint um Gesamtsumme von Transaktionen zu ziehen, gefiltert nach Start und Enddatum
# Start- und Enddatum sind optional: Standardmäßig die letzten 30 Tage
@router.get("/summary", response_model=SummaryTotals)
def get_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Gibt die Gesamtsumme von Einnahmen und Ausgaben sowie die Differenz zurück.
    Standardmäßig für die letzten 30 Tage.
    """
    #Check ob Start- und Enddaten mitgegeben wurde
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    #Nutzen des Analytics Service /services/analytics_service.py
    return analytics_service.get_summary_totals(
        db=db,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date
    )

# GET Endpoint um Kategorie Summen zu bekommen, gefiltert nach Startdatum, Enddatum,
# Gruppierung (Tag, Monat, Woche, etc.) und Typ (Ausgabe oder Einnahme)
@router.get("/category-sums", response_model=List[TimeseriesPoint])
def get_category_sums(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    group_by: GroupBy = Query(GroupBy.DAY),
    category_ids: Optional[List[int]] = Query(None),
    type: Optional[str] = Query(None, description="Filter nach 'expense' oder 'income'"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Gibt die summierten Ausgaben/Einnahmen gruppiert nach Kategorie und Zeitraum (Tag, Woche, Monat) zurück.
    Ideal für Area- und Bar-Charts.
    """
    if not end_date:
        end_date = date.today() #Wenn kein Enddatum, dann Heute
    if not start_date:
        # Standardmäßig 30 Tage bei Tag-Gruppierung, sonst mehr
        if group_by == GroupBy.MONTH:
            start_date = end_date - timedelta(days=365)
        elif group_by == GroupBy.WEEK:
            start_date = end_date - timedelta(days=90)
        else:
            start_date = end_date - timedelta(days=30)
    
    return analytics_service.get_grouped_category_sums(
        db=db,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        group_by=group_by.value,
        category_ids=category_ids,
        transaction_type=type
    )

# GET Endpoint um die größte zu ziehen. Optionaler Filter nach Kategorie, um die 
# größte Ausgabe einer Kategorie zu bekommen. Weitere Filter nach Zeiträumen.
@router.get("/largest-expense", response_model=LargestExpense)
def get_largest_expense(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Gibt die größte Ausgabe im angegebenen Zeitraum zurück.
    Standardmäßig für die letzten 30 Tage.
    """
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    expense = analytics_service.get_largest_expense(
        db=db,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        category_id=category_id
    )

    return {"expense": expense}