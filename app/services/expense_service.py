# Der Expense Service handled komplexe Funktionen für die Transaktionen
# Autor: Rose Bahar

from sqlalchemy.orm import Session
from sqlalchemy import update, delete, select, func
from typing import List
from app.models.expense import Expense
from app.schemas.expense import ExpenseUpdate, CategorySuggestionRequest

class ExpenseService:
    @staticmethod
    def bulk_update(db: Session, user_id: str, ids: List[int], data: ExpenseUpdate) -> int:
        """
        Aktualisiert mehrere Ausgaben gleichzeitig.
        Gibt die Anzahl der aktualisierten Datensätze zurück.
        """

        # Wir gleichen ab, welcher ob wir wirklich auch Änderungen in den Datensätzen kriegen
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return 0

        stmt = (
            update(Expense)
            .where(Expense.id.in_(ids))
            .where(Expense.user_id == user_id)
            .values(**update_data)
        )

        result = db.execute(stmt)
        updated_count = getattr(result, "rowcount", 0)
        db.commit()
        
        return updated_count

    @staticmethod
    def bulk_delete(db: Session, user_id: str, ids: List[int]) -> int:
        """
        Löscht mehrere Ausgaben gleichzeitig.
        Gibt die Anzahl der gelöschten Datensätze zurück.
        """

        # Wenn keine IDs angegeben sind, können wir auch nichts löschen, also return
        if not ids:
            return 0

        stmt = (
            delete(Expense)
            .where(Expense.id.in_(ids))
            .where(Expense.user_id == user_id)
        )

        result = db.execute(stmt)
        deleted_count = getattr(result, "rowcount", 0)
        db.commit()

        return deleted_count

    @staticmethod
    def suggest_categories(db: Session, user_id: str, requests: List[CategorySuggestionRequest]) -> List[dict]:
        """
        Schlägt Kategorien basierend auf der Ähnlichkeit zu vergangenen Transaktionen vor.
        Berücksichtigt dabei den Transaktionstyp (Einnahme/Ausgabe).
        """
        if not requests:
            return []

        # 1. Historische Daten laden: Häufigste Kategorie pro Beschreibung und Typ
        stmt = (
            select(
                Expense.description,
                Expense.category_id,
                Expense.type,
                func.count(Expense.id).label("count")
            )
            .where(Expense.user_id == user_id)
            .where(Expense.description.is_not(None))
            .where(Expense.category_id.is_not(None))
            .group_by(Expense.description, Expense.category_id, Expense.type)
            .order_by(func.count(Expense.id).desc())
        )
        
        history = db.execute(stmt).all()
        
        # Mapping von (Beschreibung normalisiert, Typ) zur häufigsten Kategorie
        exact_matches = {}
        for row in history:
            desc_norm = row.description.lower().strip() #klein ohne spaces am anfang oder ende
            key = (desc_norm, row.type)
            if key not in exact_matches:
                exact_matches[key] = row.category_id
        
        results = []
        for req in requests:
            desc_norm = req.description.lower().strip()
            req_type = req.type
            
            # Strategie A: Exakter Treffer (Beschreibung + Typ)
            suggested_id = exact_matches.get((desc_norm, req_type))
            confidence = 1.0 if suggested_id else 0.0
            
            # Strategie B: Substring-Treffer (nur für denselben Typ)
            if not suggested_id:
                for (hist_desc, hist_type), cat_id in exact_matches.items():
                    if hist_type != req_type:
                        continue
                        
                    # Wenn der historische Begriff im neuen vorkommt oder umgekehrt
                    # Wir prüfen nur Begriffe ab 4 Zeichen um Rauschen zu vermeiden
                    if len(hist_desc) > 3 and (hist_desc in desc_norm or desc_norm in hist_desc):
                        suggested_id = cat_id
                        confidence = 0.7
                        break
            
            results.append({
                "description": req.description,
                "suggested_category_id": suggested_id,
                "confidence": confidence
            })
            
        return results
