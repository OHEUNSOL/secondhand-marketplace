from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User
from app.routers.deps import get_current_user
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartResponse
from app.services.cart_service import CartService
from app.services.errors import ServiceError

router = APIRouter(prefix="/cart", tags=["cart"])


@router.post("")
def add_to_cart(
    payload: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CartService(db)
    try:
        item = service.add(current_user.id, payload)
        return {"id": item.id}
    except ServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.get("", response_model=CartResponse)
def list_cart(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    items = CartService(db).list(current_user.id)
    response_items = []
    total = 0
    for item in items:
        subtotal = item.quantity * item.product.price
        if item.selected:
            total += subtotal
        response_items.append(
            {
                "id": item.id,
                "product_id": item.product_id,
                "title": item.product.title,
                "status": item.product.status,
                "price": item.product.price,
                "quantity": item.quantity,
                "selected": item.selected,
                "subtotal": subtotal,
            }
        )
    return CartResponse(items=response_items, total_amount=total)


@router.patch("/{item_id}")
def update_cart_item(
    item_id: int,
    payload: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CartService(db)
    try:
        service.update(current_user.id, item_id, payload)
        return {"message": "Cart updated"}
    except ServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.delete("/{item_id}")
def delete_cart_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CartService(db)
    try:
        service.delete(current_user.id, item_id)
        return {"message": "Cart item deleted"}
    except ServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
