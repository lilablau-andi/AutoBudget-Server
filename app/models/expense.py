# Model für die Transaktionen
# Autor: Rose Bahar

from datetime import date, datetime, timezone
from sqlalchemy import String, Float, Date, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.category import Category

# Die Transaktionen ist die größte Tabelle in unserem Backend
# Sie umfasst die id, user_id, Betrag, Typ, Kategorie als Relationship,
# Beschreibung und das Ausgabedatum
# Standardmäßig gibt es außerdem noch das Erstellungsdatum
# Weiterhin gibt es für den CSV-Import noch die Spalte is_draft 
class Expense(Base):
    """
    ORM-Modell für eine Ausgabe oder Einnahme.
    Repräsentiert die Tabelle 'expenses' in der Datenbank.
    """

    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String,
        index=True,
        nullable=False,
    )
    amount: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    type: Mapped[str] = mapped_column(
        String(10),  # "expense" | "income"
        nullable=False,
    )
    category_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("categories.id"),
        nullable=True,
    )
    category: Mapped["Category"] = relationship("Category")
    description: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )
    expense_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    is_draft: Mapped[bool] = mapped_column(
        default=False,
        server_default="false",
        nullable=False,
    )
