from sqlalchemy.orm import Session

from app.models import Purchase
from app.repositories.cart_repository import CartRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.purchase_repository import PurchaseRepository
from app.services.errors import ServiceError


class PurchaseService:
    def __init__(self, db: Session):
        self.db = db
        self.product_repo = ProductRepository(db)
        self.cart_repo = CartRepository(db)
        self.purchase_repo = PurchaseRepository(db)

    def buy_now(self, buyer_id: int, product_id: int) -> Purchase:
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise ServiceError(404, "Product not found")
        if product.is_blinded:
            raise ServiceError(400, "Blinded product cannot be purchased")
        if product.seller_id == buyer_id:
            raise ServiceError(400, "Cannot buy your own product")

        if not self.product_repo.mark_sold_if_available(product.id):
            raise ServiceError(409, "Product is already sold or unavailable")

        purchase = Purchase(
            buyer_id=buyer_id,
            seller_id=product.seller_id,
            product_id=product.id,
            quantity=1,
            amount=product.price,
        )
        self.purchase_repo.create(purchase)

        cart_item = self.cart_repo.get_item(buyer_id, product.id)
        if cart_item:
            self.cart_repo.delete(cart_item)

        self.db.commit()
        return purchase

    def buy_selected_cart_items(self, buyer_id: int) -> list[Purchase]:
        items = self.cart_repo.list_selected(buyer_id)
        if not items:
            raise ServiceError(400, "No selected cart items")

        purchases: list[Purchase] = []
        for item in items:
            product = self.product_repo.get_by_id(item.product_id)
            if not product:
                continue
            if product.seller_id == buyer_id:
                continue

            if not self.product_repo.mark_sold_if_available(product.id):
                continue

            purchase = Purchase(
                buyer_id=buyer_id,
                seller_id=product.seller_id,
                product_id=product.id,
                quantity=1,
                amount=product.price,
            )
            self.purchase_repo.create(purchase)
            self.cart_repo.delete(item)
            purchases.append(purchase)

        if not purchases:
            raise ServiceError(400, "No purchasable selected items")

        self.db.commit()
        return purchases

    def my_purchases(self, buyer_id: int):
        return self.purchase_repo.list_by_buyer(buyer_id)

    def my_sales(self, seller_id: int):
        return self.purchase_repo.list_by_seller(seller_id)
