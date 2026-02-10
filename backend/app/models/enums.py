from enum import Enum


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class ProductCondition(str, Enum):
    NEW = "new"
    USED = "used"


class ProductStatus(str, Enum):
    ON_SALE = "on_sale"
    RESERVED = "reserved"
    SOLD = "sold"


class ProductCategory(str, Enum):
    ELECTRONICS = "electronics"
    CLOTHES = "clothes"
    HOME = "home"
    BOOKS = "books"
    ETC = "etc"
