# Schemas sind die Schnittstelle zwischen Backend und App
# Einfach gesagt, legen sie fest, was reindarf und was nicht
# Sie validieren und legen fest, was der Nutzer sehen kann
# Das Analytics Schema speichert keine Daten, sondern fasst diese nur zusammen und gibt
# sie berechnet zurück
# Autor: Bastian Holstein

from datetime import date
from typing import Optional, Dict
from pydantic import BaseModel
from app.schemas.expense import ExpenseRead
from enum import Enum

# Gruppierungen
class GroupBy(str, Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"

class CategoryDailySum(BaseModel):
    """
    Schema für eine Tagessumme
    """
    date: date
    sum: float
    category_name: str

    class Config:
        from_attributes = True

class TimeseriesPoint(BaseModel):
    """
    Tagessumme der Kategorien
    Beispiel: { "date": "2023-01-01", "Lebensmittel": 10.5, "Miete": 500.0, "total": 510.5 }
    """
    date: date
    values: Dict[str, float]
    total: float

#Gesamtsumme für Start- und Enddatum
class SummaryTotals(BaseModel):
    start_date: date
    end_date: date
    total_income: float
    total_expenses: float
    net_balance: float

    class Config:
        from_attributes = True

#Ausgabe der größten Ausgabe
class LargestExpense(BaseModel):
    expense: Optional[ExpenseRead] = None

    class Config:
        from_attributes = True
