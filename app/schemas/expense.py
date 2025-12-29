from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import Optional


class ExpenseCreate(BaseModel):
    """
    Schema für das Erstellen oder Aktualisieren einer Ausgabe / Einnahme.
    """
    amount: float = Field(
        ...,
        gt=0,
        description="Betrag der Ausgabe oder Einnahme (größer als 0)",
    )

    type: str = Field(
        ...,
        pattern="^(expense|income)$",
        description="Typ der Transaktion ('expense' oder 'income')",
    )

    category_id: Optional[int] = Field(
        None,
        description="ID der zugehörigen Kategorie (optional)",
    )

    description: Optional[str] = Field(
        None,
        description="Optionale Beschreibung",
    )

    expense_date: date = Field(
        ...,
        description="Datum der Ausgabe / Einnahme",
    )

    model_config = ConfigDict(
        str_min_length=1,
        str_strip_whitespace=True,
    )


class ExpenseRead(ExpenseCreate):
    """
    Schema für das Zurückgeben einer Ausgabe / Einnahme.
    """
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
