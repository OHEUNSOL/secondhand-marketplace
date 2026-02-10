from pydantic import BaseModel, Field

from app.models.enums import ProductStatus


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(ge=1, le=99)


class CartItemUpdate(BaseModel):
    quantity: int | None = Field(default=None, ge=1, le=99)
    selected: bool | None = None


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    title: str
    status: ProductStatus
    price: int
    quantity: int
    selected: bool
    subtotal: int


class CartResponse(BaseModel):
    items: list[CartItemResponse]
    total_amount: int
