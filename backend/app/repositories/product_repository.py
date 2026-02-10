from __future__ import annotations

from sqlalchemy import func, or_, select, update
from sqlalchemy.orm import Session, selectinload

from app.models import Product, ProductCategory, ProductImage
from app.models.enums import ProductStatus


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, product: Product) -> Product:
        self.db.add(product)
        self.db.flush()
        self.db.refresh(product)
        return product

    def get_by_id(self, product_id: int) -> Product | None:
        return self.db.scalar(
            select(Product)
            .options(selectinload(Product.images), selectinload(Product.seller))
            .where(Product.id == product_id)
        )

    def get_for_update(self, product_id: int) -> Product | None:
        return self.db.scalar(
            select(Product)
            .options(selectinload(Product.images), selectinload(Product.seller))
            .where(Product.id == product_id)
            .with_for_update()
        )

    def list(
        self,
        *,
        page: int,
        page_size: int,
        keyword: str | None,
        category: ProductCategory | None,
        sort: str,
        include_blinded: bool,
    ) -> tuple[int, list[Product]]:
        filters = []
        if keyword:
            filters.append(
                or_(
                    Product.title.ilike(f"%{keyword}%"),
                    Product.description.ilike(f"%{keyword}%"),
                )
            )
        if category:
            filters.append(Product.category == category)
        if not include_blinded:
            filters.append(Product.is_blinded.is_(False))

        sort_expr = Product.created_at.desc()
        if sort == "price_asc":
            sort_expr = Product.price.asc()
        elif sort == "price_desc":
            sort_expr = Product.price.desc()

        total_stmt = select(func.count(Product.id))
        if filters:
            total_stmt = total_stmt.where(*filters)

        stmt = (
            select(Product)
            .options(selectinload(Product.images), selectinload(Product.seller))
            .order_by(sort_expr)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        if filters:
            stmt = stmt.where(*filters)

        total = int(self.db.scalar(total_stmt) or 0)
        items = list(self.db.scalars(stmt).all())
        return total, items

    def replace_images(self, product: Product, image_urls: list[str]) -> None:
        product.images.clear()
        for image_url in image_urls:
            product.images.append(ProductImage(image_url=image_url))

    def mark_sold_if_available(self, product_id: int) -> bool:
        result = self.db.execute(
            update(Product)
            .where(
                Product.id == product_id,
                Product.status == ProductStatus.ON_SALE,
                Product.is_blinded.is_(False),
            )
            .values(status=ProductStatus.SOLD)
        )
        return bool(result.rowcount)
