import os
import unittest
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace

# Configure env before app imports.
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_secondhand.db")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
os.environ.setdefault("JWT_EXPIRE_MINUTES", "120")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:3000")
os.environ.setdefault("ADMIN_EMAIL", "admin@example.com")
os.environ.setdefault("ADMIN_PASSWORD", "Admin1234!")
os.environ.setdefault("ADMIN_NICKNAME", "market-admin")

from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.core.security import decode_token, hash_password, verify_password
from app.models import Product, ProductCondition, ProductStatus, Purchase, User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.cart import CartItemCreate, CartItemUpdate
from app.schemas.product import ProductCreate, ProductUpdate
from app.services.auth_service import AuthService
from app.services.cart_service import CartService
from app.services.errors import ServiceError
from app.services.product_service import ProductService
from app.services.purchase_service import PurchaseService


class RequirementsServiceTest(unittest.TestCase):
    def setUp(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        self.db = SessionLocal()

        # Seed admin user (same behavior as app startup).
        admin_user = User(
            email=settings.admin_email,
            nickname=settings.admin_nickname,
            password_hash=hash_password(settings.admin_password),
            role=UserRole.ADMIN,
        )
        self.db.add(admin_user)
        self.db.commit()

    def tearDown(self):
        self.db.close()

    @classmethod
    def tearDownClass(cls):
        engine.dispose()
        if os.path.exists("test_secondhand.db"):
            os.remove("test_secondhand.db")

    def signup_and_login(self, email: str, nickname: str, password: str) -> User:
        auth_service = AuthService(self.db)
        user = auth_service.signup(
            SimpleNamespace(email=email, nickname=nickname, password=password)
        )
        token = auth_service.login(SimpleNamespace(email=email, password=password))
        subject = decode_token(token)
        self.assertEqual(int(subject), user.id)
        return user

    def create_product(self, seller_id: int, title: str, price: int, category: str = "electronics") -> Product:
        product_service = ProductService(self.db)
        return product_service.create(
            seller_id,
            ProductCreate(
                title=title,
                price=price,
                description=f"{title} description",
                category=category,
                condition="used",
                image_urls=["https://example.com/image.jpg"],
            ),
        )

    def test_1_auth_signup_login_jwt_bcrypt_admin_seed(self):
        user = self.signup_and_login("user1@example.com", "user1", "Password123!")

        db_user = UserRepository(self.db).get_by_id(user.id)
        self.assertIsNotNone(db_user)
        self.assertNotEqual(db_user.password_hash, "Password123!")
        self.assertTrue(verify_password("Password123!", db_user.password_hash))

        admin = UserRepository(self.db).get_by_email("admin@example.com")
        self.assertIsNotNone(admin)
        self.assertEqual(admin.role, UserRole.ADMIN)

    def test_2_product_register_update_delete_and_owner_rule(self):
        seller = self.signup_and_login("seller@example.com", "seller", "Password123!")
        buyer = self.signup_and_login("buyer@example.com", "buyer", "Password123!")

        product = self.create_product(seller.id, "iPad Mini", 300000)
        product_service = ProductService(self.db)

        updated = product_service.update(
            seller.id,
            product.id,
            ProductUpdate(price=280000, status="reserved"),
        )
        self.assertEqual(updated.price, 280000)
        self.assertEqual(updated.status, ProductStatus.RESERVED)

        with self.assertRaises(ServiceError):
            product_service.delete(buyer.id, product.id)

        product_service.delete(seller.id, product.id)
        with self.assertRaises(ServiceError):
            product_service.get(product.id)

    def test_3_product_list_search_sort_pagination(self):
        seller = self.signup_and_login("seller2@example.com", "seller2", "Password123!")

        self.create_product(seller.id, "Galaxy Watch", 200000, "electronics")
        self.create_product(seller.id, "Programming Book", 15000, "books")
        self.create_product(seller.id, "Desk Lamp", 30000, "home")

        product_service = ProductService(self.db)

        total, items = product_service.list(
            page=1,
            page_size=2,
            keyword=None,
            category=None,
            sort="latest",
            include_blinded=False,
        )
        self.assertEqual(total, 3)
        self.assertEqual(len(items), 2)

        _, keyword_items = product_service.list(
            page=1,
            page_size=10,
            keyword="Book",
            category=None,
            sort="latest",
            include_blinded=False,
        )
        self.assertTrue(any("Book" in item.title for item in keyword_items))

        _, category_items = product_service.list(
            page=1,
            page_size=10,
            keyword=None,
            category="books",
            sort="latest",
            include_blinded=False,
        )
        self.assertTrue(all(item.category == "books" for item in category_items))

        _, asc_items = product_service.list(
            page=1,
            page_size=10,
            keyword=None,
            category=None,
            sort="price_asc",
            include_blinded=False,
        )
        asc_prices = [item.price for item in asc_items]
        self.assertEqual(asc_prices, sorted(asc_prices))

        _, desc_items = product_service.list(
            page=1,
            page_size=10,
            keyword=None,
            category=None,
            sort="price_desc",
            include_blinded=False,
        )
        desc_prices = [item.price for item in desc_items]
        self.assertEqual(desc_prices, sorted(desc_prices, reverse=True))

    def test_4_product_detail_cart_and_buy_now(self):
        seller = self.signup_and_login("seller3@example.com", "seller3", "Password123!")
        buyer = self.signup_and_login("buyer3@example.com", "buyer3", "Password123!")

        product = self.create_product(seller.id, "MacBook Air", 800000)
        fetched = ProductService(self.db).get(product.id)
        self.assertEqual(fetched.seller.nickname, "seller3")

        cart_service = CartService(self.db)
        cart_service.add(buyer.id, CartItemCreate(product_id=product.id, quantity=1))

        purchase = PurchaseService(self.db).buy_now(buyer.id, product.id)
        self.assertEqual(purchase.amount, 800000)

        sold = self.db.query(Product).filter(Product.id == product.id).first()
        self.assertEqual(sold.status, ProductStatus.SOLD)

    def test_5_cart_update_delete_total_and_checkout_selected(self):
        seller = self.signup_and_login("seller4@example.com", "seller4", "Password123!")
        buyer = self.signup_and_login("buyer4@example.com", "buyer4", "Password123!")

        p1 = self.create_product(seller.id, "Keyboard", 50000)
        p2 = self.create_product(seller.id, "Mouse", 30000)

        cart_service = CartService(self.db)
        cart_service.add(buyer.id, CartItemCreate(product_id=p1.id, quantity=1))
        cart_service.add(buyer.id, CartItemCreate(product_id=p2.id, quantity=1))

        items = cart_service.list(buyer.id)
        self.assertEqual(len(items), 2)

        p1_item_id = next(item.id for item in items if item.product_id == p1.id)
        p2_item_id = next(item.id for item in items if item.product_id == p2.id)

        cart_service.update(buyer.id, p1_item_id, CartItemUpdate(quantity=2))
        cart_service.update(buyer.id, p2_item_id, CartItemUpdate(selected=False))

        refreshed = cart_service.list(buyer.id)
        selected_total = sum(
            item.quantity * item.product.price for item in refreshed if item.selected
        )
        self.assertEqual(selected_total, 100000)

        purchases = PurchaseService(self.db).buy_selected_cart_items(buyer.id)
        self.assertEqual(len(purchases), 1)
        self.assertEqual(purchases[0].amount, 100000)

        cart_service.delete(buyer.id, p2_item_id)
        left = cart_service.list(buyer.id)
        self.assertEqual(len(left), 0)

    def test_6_purchase_history_and_sales_history(self):
        seller = self.signup_and_login("seller5@example.com", "seller5", "Password123!")
        buyer = self.signup_and_login("buyer5@example.com", "buyer5", "Password123!")

        product = self.create_product(seller.id, "Gaming Chair", 120000)
        PurchaseService(self.db).buy_now(buyer.id, product.id)

        my_purchases = PurchaseService(self.db).my_purchases(buyer.id)
        self.assertTrue(any(item.product_id == product.id for item in my_purchases))

        my_sales = PurchaseService(self.db).my_sales(seller.id)
        self.assertTrue(any(item.product_id == product.id for item in my_sales))

    def test_7_admin_blind_unblind_visibility_logic(self):
        seller = self.signup_and_login("seller6@example.com", "seller6", "Password123!")
        self.signup_and_login("user6@example.com", "user6", "Password123!")

        product = self.create_product(seller.id, "Canon Camera", 450000)
        product_service = ProductService(self.db)

        blinded = product_service.blind(product.id, "정책 위반 의심")
        self.assertTrue(blinded.is_blinded)
        self.assertEqual(blinded.blind_reason, "정책 위반 의심")

        _, public_items = product_service.list(
            page=1,
            page_size=10,
            keyword=None,
            category=None,
            sort="latest",
            include_blinded=False,
        )
        self.assertTrue(all(item.id != product.id for item in public_items))

        _, admin_items = product_service.list(
            page=1,
            page_size=10,
            keyword=None,
            category=None,
            sort="latest",
            include_blinded=True,
        )
        self.assertTrue(any(item.id == product.id for item in admin_items))

        unblinded = product_service.unblind(product.id)
        self.assertFalse(unblinded.is_blinded)
        self.assertIsNone(unblinded.blind_reason)

    def test_optional_product_fields_and_status_values(self):
        seller = self.signup_and_login("seller7@example.com", "seller7", "Password123!")

        product_service = ProductService(self.db)
        product = product_service.create(
            seller.id,
            ProductCreate(
                title="Notebook",
                price=7000,
                description="used notebook",
                category="books",
                condition=ProductCondition.USED,
                image_urls=[],
            ),
        )
        self.assertEqual(product.status, ProductStatus.ON_SALE)

    def test_concurrent_buy_prevent_double_purchase(self):
        seller = self.signup_and_login("seller8@example.com", "seller8", "Password123!")
        buyer1 = self.signup_and_login("buyer8a@example.com", "buyer8a", "Password123!")
        buyer2 = self.signup_and_login("buyer8b@example.com", "buyer8b", "Password123!")

        product = self.create_product(seller.id, "Concurrent Item", 99000)

        def attempt_buy(buyer_id: int) -> bool:
            local_db = SessionLocal()
            try:
                PurchaseService(local_db).buy_now(buyer_id, product.id)
                return True
            except ServiceError:
                return False
            finally:
                local_db.close()

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(attempt_buy, [buyer1.id, buyer2.id]))

        self.assertEqual(sum(1 for result in results if result), 1)

        verify_db = SessionLocal()
        try:
            sold_product = verify_db.query(Product).filter(Product.id == product.id).first()
            self.assertEqual(sold_product.status, ProductStatus.SOLD)

            purchases = verify_db.query(Purchase).filter(Purchase.product_id == product.id).all()
            self.assertEqual(len(purchases), 1)
        finally:
            verify_db.close()


if __name__ == "__main__":
    unittest.main()
