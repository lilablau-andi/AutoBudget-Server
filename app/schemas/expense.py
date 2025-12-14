from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import Optional


class ExpenseCreate(BaseModel):
    """
    Schema für das Erstellen einer Ausgabe.
    Validiert die Daten, die beim Anlegen einer Ausgabe erwartet werden.
    """
    amount: float = Field(..., gt=0, description="Betrag der Ausgabe (größer als 0)")
    type: str = Field(..., pattern="^(expense|income)$", description="Typ der Transaktion ('expense' oder 'income')")
    category: str = Field(..., description="Kategorie der Ausgabe")
    description: Optional[str] = Field(None, description="Optional: Beschreibung der Ausgabe")
    expense_date: date = Field(..., description="Datum der Ausgabe")

    model_config = ConfigDict(
        str_min_length=1,
        str_strip_whitespace=True
    )


class ExpenseRead(ExpenseCreate):
    """
    Schema für das Abrufen von Ausgaben.
    Erbt von ExpenseCreate, aber fügt den `id` und `created_at` hinzu.
    """
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)  # Ermöglicht die Rückgabe von ORM-Objekten als Response
