from fastapi import APIRouter

# Importiere Feature-Router (kommen als Nächstes)
from app.api.v1 import expenses, categories, budgets, goals, analytics

router = APIRouter()

router.include_router(expenses.router, prefix="/expenses", tags=["Expenses"])
router.include_router(categories.router, prefix="/categories", tags=["Categories"])
#router.include_router(budgets.router, prefix="/budgets", tags=["Budgets"])
#router.include_router(goals.router, prefix="/goals", tags=["Goals"])
#router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])