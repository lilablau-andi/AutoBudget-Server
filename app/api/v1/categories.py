from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate

router = APIRouter()


@router.post(
    "/",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
)
def create_category(
    category_in: CategoryCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Erstellt eine neue Kategorie für den aktuellen User.
    """

    category = Category(
        user_id=user_id,
        type=category_in.type,
        name=category_in.name,
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return category

@router.get(
    "/",
    response_model=list[CategoryRead],
)
def list_categories(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Gibt alle Kategorien des aktuellen Users zurück.
    Sortiert nach Datum (neueste zuerst).
    """

    stmt = (
        select(Category)
        .where(Category.user_id == user_id)
    )

    categories = db.execute(stmt).scalars().all()

    return categories

@router.put(
    "/{category_id}",
    response_model=CategoryRead,
)
def update_category(
    category_id: int,
    category_in: CategoryCreate,  # Changed to CategoryCreate for full update
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Überschreibt eine bestehende Kategorie des aktuellen Users (Full Update).
    """

    category = db.get(Category, category_id)

    if not category or category.user_id != user_id:
        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )

    # Bei PUT erwarten wir alle Felder
    category.name = category_in.name
    category.type = category_in.type

    db.commit()
    db.refresh(category)

    return category

@router.patch(
    "/{category_id}",
    response_model=CategoryRead,
)
def patch_category(
    category_id: int,
    category_in: CategoryUpdate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Aktualisiert eine bestehende Kategorie des aktuellen Users (Teil-Update).
    Nur die übergebenen Felder werden geändert.
    """

    category = db.get(Category, category_id)

    if not category or category.user_id != user_id:
        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )

    # Nur Felder aktualisieren, die explizit im Body gesendet wurden
    update_data = category_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)

    db.commit()
    db.refresh(category)

    return category

@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Löscht eine Kategorie des aktuellen Users.
    """

    category = db.get(Category, category_id)

    if not category or category.user_id != user_id:
        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )

    db.delete(category)
    db.commit()

    return None