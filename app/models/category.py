# Model für die Categories
# Autor: Bastian Holstein

from datetime import date, datetime, timezone
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

# Die Tabelle Kategorien besteht aus id, user_id, Name, Typ (Ausgabe oder Einkommen) und 
# Erstellungsdatum
class Category(Base):
    __tablename__ = "categories"


    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String,
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    type: Mapped[str] = mapped_column(
        String(10),  # "expense" | "income"
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
