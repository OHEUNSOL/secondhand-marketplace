from sqlalchemy.orm import Session

from app.models import Product, ProductCategory
from app.models.enums import ProductStatus
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate
from app.services.errors import ServiceError


class ProductService:
    def __init__(self, db: Session):
        self.db = db
        self.product_repo = ProductRepository(db)

    def create(self, seller_id: int, payload: ProductCreate) -> Product:
        if len(payload.image_urls) > 5:
            raise ServiceError(400, "At most 5 images are allowed")

        product = Product(
            seller_id=seller_id,
            title=payload.title,
            price=payload.price,
            description=payload.description,
            category=payload.category,
            condition=payload.condition,
        )
        self.product_repo.create(product)
        self.product_repo.replace_images(product, payload.image_urls)
        self.db.commit()
        self.db.refresh(product)
        return self.product_repo.get_by_id(product.id) or product

    def list(
        self,
        *,
        page: int,
        page_size: int,
        keyword: str | None,
        category: ProductCategory | None,
        sort: str,
        include_blinded: bool,
    ):
        return self.product_repo.list(
            page=page,
            page_size=page_size,
            keyword=keyword,
            category=category,
            sort=sort,
            include_blinded=include_blinded,
        )

    def get(self, product_id: int) -> Product:
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise ServiceError(404, "Product not found")
        return product

    def update(self, user_id: int, product_id: int, payload: ProductUpdate) -> Product:
        product = self.get(product_id)
        if product.seller_id != user_id:
            raise ServiceError(403, "Only seller can update this product")
        if product.status == ProductStatus.SOLD:
            raise ServiceError(400, "Sold product cannot be updated")

        data = payload.model_dump(exclude_unset=True)
        image_urls = data.pop("image_urls", None)
        for key, value in data.items():
            setattr(product, key, value)
        if image_urls is not None:
            if len(image_urls) > 5:
                raise ServiceError(400, "At most 5 images are allowed")
            self.product_repo.replace_images(product, image_urls)

        self.db.commit()
        self.db.refresh(product)
        return self.get(product.id)

    def delete(self, user_id: int, product_id: int) -> None:
        product = self.get(product_id)
        if product.seller_id != user_id:
            raise ServiceError(403, "Only seller can delete this product")
        if product.status == ProductStatus.SOLD:
            raise ServiceError(400, "Sold product cannot be deleted")
        self.db.delete(product)
        self.db.commit()

    def blind(self, product_id: int, reason: str) -> Product:
        product = self.get(product_id)
        product.is_blinded = True
        product.blind_reason = reason
        self.db.commit()
        self.db.refresh(product)
        return product

    def unblind(self, product_id: int) -> Product:
        product = self.get(product_id)
        product.is_blinded = False
        product.blind_reason = None
        self.db.commit()
        self.db.refresh(product)
        return product
