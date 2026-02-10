from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import ProductCategory, User
from app.models.enums import UserRole
from app.routers.deps import get_current_user, get_current_user_optional
from app.schemas.product import (
    ProductCreate,
    ProductDetail,
    ProductListResponse,
    ProductSummary,
    ProductUpdate,
)
from app.services.errors import ServiceError
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"])


def to_summary(item) -> ProductSummary:
    return ProductSummary(
        id=item.id,
        title=item.title,
        price=item.price,
        category=item.category,
        condition=item.condition,
        status=item.status,
        is_blinded=item.is_blinded,
        seller_nickname=item.seller.nickname,
        thumbnail_url=item.images[0].image_url if item.images else None,
        created_at=item.created_at,
    )


def to_detail(item) -> ProductDetail:
    return ProductDetail(
        id=item.id,
        title=item.title,
        price=item.price,
        description=item.description,
        category=item.category,
        condition=item.condition,
        status=item.status,
        is_blinded=item.is_blinded,
        blind_reason=item.blind_reason,
        seller_id=item.seller_id,
        seller_nickname=item.seller.nickname,
        image_urls=[image.image_url for image in item.images],
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.post("", response_model=ProductDetail)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProductService(db)
    try:
        return to_detail(service.create(current_user.id, payload))
    except ServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.get("", response_model=ProductListResponse)
def list_products(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    keyword: str | None = Query(default=None),
    category: ProductCategory | None = Query(default=None),
    sort: str = Query(default="latest", pattern="^(latest|price_asc|price_desc)$"),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    service = ProductService(db)
    include_blinded = bool(current_user and current_user.role == UserRole.ADMIN)
    total, items = service.list(
        page=page,
        page_size=page_size,
        keyword=keyword,
        category=category,
        sort=sort,
        include_blinded=include_blinded,
    )
    return ProductListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[to_summary(item) for item in items],
    )


@router.get("/{product_id}", response_model=ProductDetail)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    service = ProductService(db)
    try:
        product = service.get(product_id)
        if product.is_blinded and (
            not current_user or current_user.role != UserRole.ADMIN
        ):
            raise HTTPException(status_code=403, detail="Blinded product")
        return to_detail(product)
    except ServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.patch("/{product_id}", response_model=ProductDetail)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProductService(db)
    try:
        return to_detail(service.update(current_user.id, product_id, payload))
    except ServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProductService(db)
    try:
        service.delete(current_user.id, product_id)
        return {"message": "Product deleted"}
    except ServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
