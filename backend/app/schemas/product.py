from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import ProductCategory, ProductCondition, ProductStatus


class ProductCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    price: int = Field(ge=1)
    description: str = Field(min_length=1)
    category: ProductCategory
    condition: ProductCondition
    image_urls: list[str] = Field(default_factory=list, max_length=5)


class ProductUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    price: int | None = Field(default=None, ge=1)
    description: str | None = Field(default=None, min_length=1)
    category: ProductCategory | None = None
    condition: ProductCondition | None = None
    status: ProductStatus | None = None
    image_urls: list[str] | None = Field(default=None, max_length=5)


class ProductSummary(BaseModel):
    id: int
    title: str
    price: int
    category: ProductCategory
    condition: ProductCondition
    status: ProductStatus
    is_blinded: bool
    seller_nickname: str
    thumbnail_url: str | None
    created_at: datetime


class ProductDetail(BaseModel):
    id: int
    title: str
    price: int
    description: str
    category: ProductCategory
    condition: ProductCondition
    status: ProductStatus
    is_blinded: bool
    blind_reason: str | None
    seller_id: int
    seller_nickname: str
    image_urls: list[str]
    created_at: datetime
    updated_at: datetime


class ProductListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[ProductSummary]
