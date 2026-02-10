from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User
from app.routers.deps import get_current_user
from app.schemas.purchase import PurchaseResponse
from app.services.errors import ServiceError
from app.services.purchase_service import PurchaseService

router = APIRouter(prefix="/purchases", tags=["purchases"])


@router.post("/buy-now/{product_id}")
def buy_now(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        purchase = PurchaseService(db).buy_now(current_user.id, product_id)
        return {"purchase_id": purchase.id}
    except ServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.post("/checkout-selected")
def checkout_selected(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        purchases = PurchaseService(db).buy_selected_cart_items(current_user.id)
        return {"purchase_ids": [purchase.id for purchase in purchases]}
    except ServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.get("/me", response_model=PurchaseResponse)
def my_purchases(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    purchases = PurchaseService(db).my_purchases(current_user.id)
    return {
        "purchases": [
            {
                "id": purchase.id,
                "product_id": purchase.product_id,
                "product_title": purchase.product.title,
                "quantity": purchase.quantity,
                "amount": purchase.amount,
                "purchased_at": purchase.purchased_at,
            }
            for purchase in purchases
        ]
    }


@router.get("/sales/me", response_model=PurchaseResponse)
def my_sales(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    purchases = PurchaseService(db).my_sales(current_user.id)
    return {
        "purchases": [
            {
                "id": purchase.id,
                "product_id": purchase.product_id,
                "product_title": purchase.product.title,
                "quantity": purchase.quantity,
                "amount": purchase.amount,
                "purchased_at": purchase.purchased_at,
            }
            for purchase in purchases
        ]
    }
