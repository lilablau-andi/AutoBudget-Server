from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import Optional, List
from app.schemas.common import PaginatedResponse



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


class ExpenseUpdate(BaseModel):
    """
    Schema für das Aktualisieren einer Ausgabe / Einnahme.
    Alle Felder sind optional, um Teil-Updates (PATCH-Logik) zu ermöglichen.
    """
    amount: Optional[float] = Field(
        None,
        gt=0,
        description="Betrag der Ausgabe oder Einnahme (größer als 0)",
    )

    type: Optional[str] = Field(
        None,
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

    expense_date: Optional[date] = Field(
        None,
        description="Datum der Ausgabe / Einnahme",
    )

    model_config = ConfigDict(
        str_min_length=1,
        str_strip_whitespace=True,
    )


from app.schemas.category import CategoryRead

class ExpenseRead(ExpenseCreate):
    """
    Schema für das Zurückgeben einer Ausgabe / Einnahme.
    """
    id: int
    created_at: datetime
    category: Optional[CategoryRead] = None

    model_config = ConfigDict(from_attributes=True)


class ExpensePaginated(PaginatedResponse[ExpenseRead]):
    """
    Schema für die paginierte Rückgabe von Ausgaben.
    """
    pass

