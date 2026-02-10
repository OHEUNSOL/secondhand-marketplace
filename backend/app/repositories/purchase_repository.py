from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Purchase


class PurchaseRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, purchase: Purchase) -> Purchase:
        self.db.add(purchase)
        self.db.flush()
        self.db.refresh(purchase)
        return purchase

    def list_by_buyer(self, buyer_id: int) -> list[Purchase]:
        return list(
            self.db.scalars(
                select(Purchase)
                .options(selectinload(Purchase.product))
                .where(Purchase.buyer_id == buyer_id)
                .order_by(Purchase.purchased_at.desc())
            ).all()
        )

    def list_by_seller(self, seller_id: int) -> list[Purchase]:
        return list(
            self.db.scalars(
                select(Purchase)
                .options(selectinload(Purchase.product))
                .where(Purchase.seller_id == seller_id)
                .order_by(Purchase.purchased_at.desc())
            ).all()
        )
