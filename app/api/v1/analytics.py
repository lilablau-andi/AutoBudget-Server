from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.analytics import CategoryDailySum
from app.services import analytics_service

router = APIRouter()

@router.get("/category-sums", response_model=List[CategoryDailySum])
def get_category_sums(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category_ids: Optional[List[int]] = Query(None),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Gibt die summierten Ausgaben pro Kategorie und Tag zurück.
    Standardmäßig für die letzten 30 Tage.
    """
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    return analytics_service.get_category_daily_sums(
        db=db,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        category_ids=category_ids
    )