from fastapi import FastAPI
from app.api.v1 import expenses

app = FastAPI(title="Ausgaben-Manager API")

app.include_router(expenses.router, prefix="/api/v1/expenses")
