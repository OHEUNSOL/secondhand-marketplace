from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.routers.deps import require_admin
from app.schemas.admin import BlindRequest
from app.services.errors import ServiceError
from app.services.product_service import ProductService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/products")
def list_all_products(db: Session = Depends(get_db), _: object = Depends(require_admin)):
    total, items = ProductService(db).list(
        page=1,
        page_size=200,
        keyword=None,
        category=None,
        sort="latest",
        include_blinded=True,
    )
    return {
        "total": total,
        "items": [
            {
                "id": item.id,
                "title": item.title,
                "status": item.status,
                "is_blinded": item.is_blinded,
                "blind_reason": item.blind_reason,
                "seller_nickname": item.seller.nickname,
            }
            for item in items
        ],
    }


@router.post("/products/{product_id}/blind")
def blind_product(
    product_id: int,
    payload: BlindRequest,
    db: Session = Depends(get_db),
    _: object = Depends(require_admin),
):
    try:
        product = ProductService(db).blind(product_id, payload.reason)
        return {"id": product.id, "is_blinded": product.is_blinded, "reason": product.blind_reason}
    except ServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.post("/products/{product_id}/unblind")
def unblind_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_admin),
):
    try:
        product = ProductService(db).unblind(product_id)
        return {"id": product.id, "is_blinded": product.is_blinded}
    except ServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
