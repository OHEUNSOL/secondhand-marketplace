from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import CartItem


class CartRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_item(self, user_id: int, product_id: int) -> CartItem | None:
        return self.db.scalar(
            select(CartItem).where(CartItem.user_id == user_id, CartItem.product_id == product_id)
        )

    def get_item_by_id(self, user_id: int, cart_item_id: int) -> CartItem | None:
        return self.db.scalar(
            select(CartItem)
            .options(selectinload(CartItem.product))
            .where(CartItem.id == cart_item_id, CartItem.user_id == user_id)
        )

    def list_items(self, user_id: int) -> list[CartItem]:
        return list(
            self.db.scalars(
                select(CartItem)
                .options(selectinload(CartItem.product))
                .where(CartItem.user_id == user_id)
                .order_by(CartItem.created_at.desc())
            ).all()
        )

    def list_selected(self, user_id: int) -> list[CartItem]:
        return list(
            self.db.scalars(
                select(CartItem)
                .options(selectinload(CartItem.product))
                .where(CartItem.user_id == user_id, CartItem.selected.is_(True))
            ).all()
        )

    def create(self, item: CartItem) -> CartItem:
        self.db.add(item)
        self.db.flush()
        self.db.refresh(item)
        return item

    def delete(self, item: CartItem) -> None:
        self.db.delete(item)
