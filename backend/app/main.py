from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.core.errors import (
    http_error_response,
    internal_error_response,
    service_error_response,
    validation_error_response,
)
from app.core.security import hash_password
from app.models import User, UserRole
from app.routers import admin, auth, cart, products, purchases
from app.services.errors import ServiceError

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.email == settings.admin_email).first()
        if not admin_user:
            admin_user = User(
                email=settings.admin_email,
                nickname=settings.admin_nickname,
                password_hash=hash_password(settings.admin_password),
                role=UserRole.ADMIN,
            )
            db.add(admin_user)
            db.commit()
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.exception_handler(ServiceError)
def handle_service_error(request: Request, exc: ServiceError):
    return service_error_response(request, exc)


@app.exception_handler(HTTPException)
def handle_http_error(request: Request, exc: HTTPException):
    return http_error_response(request, exc)


@app.exception_handler(RequestValidationError)
def handle_validation_error(request: Request, exc: RequestValidationError):
    return validation_error_response(request, exc)


@app.exception_handler(Exception)
def handle_internal_error(request: Request, _: Exception):
    return internal_error_response(request)


app.include_router(auth.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(purchases.router)
app.include_router(admin.router)
