# API Konfiguration für die REST Endpoints
# Autor: Andrej Bobb

from fastapi import APIRouter

from app.api.v1 import expenses, categories, budgets, analytics

# APIRouter ist eine Funktion von Fastapi, die Adressen der Endpoints festlegt.
# Beispielsweise können wir über /expenses die REST-Requests für die Transaktionen ansteuern
router = APIRouter()

# Hier werden die API Adressen festgelegt, über die die REST API läuft,
# Die Tags sind für die /docs bzw. /redoc
router.include_router(expenses.router, prefix="/expenses", tags=["Expenses"])
router.include_router(categories.router, prefix="/categories", tags=["Categories"])
router.include_router(budgets.router, prefix="/budgets", tags=["Budgets"])
router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])