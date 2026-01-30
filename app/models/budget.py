# Modell für die Budget Tabellen. Models beschreibt, wie die Daten in der Datenbank liegen.
# Autor: Andrej Bobb

from datetime import datetime, timezone
from sqlalchemy import String, Float, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from typing import TYPE_CHECKING

# Hier verhindern wir einen zirkulären Import mit Category
if TYPE_CHECKING:
    from app.models.category import Category

# Budget hat die folgende Struktur: id, user_id, category_id, kategorie als relationship, 
# Maximalbetrag und die Periode. Außerdem gibt es Standardmäßig noch das Erstellungsdatum
class Budget(Base):
    __tablename__ = "budgets"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    
    category_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("categories.id"), 
        nullable=False
    )
    category: Mapped["Category"] = relationship("Category")
    
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    period: Mapped[str] = mapped_column(String, default="monthly", nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
