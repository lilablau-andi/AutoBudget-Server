from datetime import date
from pydantic import BaseModel

class CategoryDailySum(BaseModel):
    date: date
    sum: float
    category_name: str

    class Config:
        from_attributes = True
