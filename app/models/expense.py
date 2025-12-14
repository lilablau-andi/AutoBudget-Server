# jede Ausgabe gehört genau einem User, jede Ausgabe hat eine Kategorie, 
# Einnahmen/Ausgaben unterscheiden wir über type
# Supabase Auth liefert uns die user_id (UUID als String)

from datetime import date, datetime, timezone

from sqlalchemy import String, Float, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Expense(Base):
    """
    ORM-Modell für eine Ausgabe oder Einnahme.
    Repräsentiert die Tabelle 'expenses' in der Datenbank.
    """

    __tablename__ = "expenses"

    # -------------------------------------------------
    # Primärschlüssel
    # -------------------------------------------------
    id: Mapped[int] = mapped_column(primary_key=True)

    # -------------------------------------------------
    # Supabase User
    # -------------------------------------------------
    user_id: Mapped[str] = mapped_column(
        String,
        index=True,
        nullable=False,
    )

    # -------------------------------------------------
    # Fachliche Felder
    # -------------------------------------------------
    amount: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    type: Mapped[str] = mapped_column(
        String(10),  # "expense" | "income"
        nullable=False,
    )

    category: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    expense_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    # -------------------------------------------------
    # Metadaten
    # -------------------------------------------------
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
