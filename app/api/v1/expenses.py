from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_expenses():
    return [{"id": 1, "amount": 12.50, "category": "Essen"}]
