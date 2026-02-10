from sqlalchemy.orm import Session

from app.models import CartItem, ProductStatus
from app.repositories.cart_repository import CartRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.cart import CartItemCreate, CartItemUpdate
from app.services.errors import ServiceError


class CartService:
    def __init__(self, db: Session):
        self.db = db
        self.cart_repo = CartRepository(db)
        self.product_repo = ProductRepository(db)

    def add(self, user_id: int, payload: CartItemCreate) -> CartItem:
        product = self.product_repo.get_by_id(payload.product_id)
        if not product:
            raise ServiceError(404, "Product not found")
        if product.status != ProductStatus.ON_SALE or product.is_blinded:
            raise ServiceError(400, "Product is not available")
        if product.seller_id == user_id:
            raise ServiceError(400, "Cannot add your own product")

        item = self.cart_repo.get_item(user_id, payload.product_id)
        if item:
            item.quantity = 1
            item.selected = True
        else:
            item = CartItem(
                user_id=user_id,
                product_id=payload.product_id,
                quantity=1,
                selected=True,
            )
            self.cart_repo.create(item)

        self.db.commit()
        return self.cart_repo.get_item_by_id(user_id, item.id) or item

    def list(self, user_id: int) -> list[CartItem]:
        return self.cart_repo.list_items(user_id)

    def update(self, user_id: int, item_id: int, payload: CartItemUpdate) -> CartItem:
        item = self.cart_repo.get_item_by_id(user_id, item_id)
        if not item:
            raise ServiceError(404, "Cart item not found")

        if payload.quantity is not None:
            if payload.quantity != 1:
                raise ServiceError(400, "Secondhand item quantity must be 1")
            item.quantity = payload.quantity
        if payload.selected is not None:
            item.selected = payload.selected

        self.db.commit()
        return self.cart_repo.get_item_by_id(user_id, item.id) or item

    def delete(self, user_id: int, item_id: int) -> None:
        item = self.cart_repo.get_item_by_id(user_id, item_id)
        if not item:
            raise ServiceError(404, "Cart item not found")
        self.cart_repo.delete(item)
        self.db.commit()
