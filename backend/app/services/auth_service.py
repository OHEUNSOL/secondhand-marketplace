from typing import Any

from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models import User, UserRole
from app.repositories.user_repository import UserRepository
from app.services.errors import ServiceError


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def signup(self, data: Any) -> User:
        if self.user_repo.get_by_email(data.email):
            raise ServiceError(409, "Email already exists")
        if self.user_repo.get_by_nickname(data.nickname):
            raise ServiceError(409, "Nickname already exists")

        user = User(
            email=data.email,
            nickname=data.nickname,
            password_hash=hash_password(data.password),
            role=UserRole.USER,
        )
        self.user_repo.create(user)
        self.db.commit()
        return user

    def login(self, data: Any) -> str:
        user = self.user_repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.password_hash):
            raise ServiceError(401, "Invalid email or password")
        return create_access_token(str(user.id))
