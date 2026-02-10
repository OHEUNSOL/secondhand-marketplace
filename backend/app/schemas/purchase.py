from datetime import datetime

from pydantic import BaseModel


class PurchaseItem(BaseModel):
    id: int
    product_id: int
    product_title: str
    quantity: int
    amount: int
    purchased_at: datetime


class PurchaseResponse(BaseModel):
    purchases: list[PurchaseItem]
