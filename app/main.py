from fastapi import FastAPI
from app.core.config import settings
from app.core.database import Base, engine

from app.models.user import User
from app.models.customer import Customer
from app.models.supplier import Supplier
from app.models.product import Product
from app.models.trade_order import TradeOrder
from app.models.shipment import Shipment

from app.api.users import router as users_router
from app.api.auth import router as auth_router
from app.api.customers import router as customers_router
from app.api.suppliers import router as suppliers_router
from app.api.products import router as products_router
from app.api.orders import router as orders_router
from app.api.shipments import router as shipments_router
from app.api.analytics import router as analytics_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME)

app.include_router(users_router)
app.include_router(auth_router)
app.include_router(customers_router)
app.include_router(suppliers_router)
app.include_router(products_router)
app.include_router(orders_router)
app.include_router(shipments_router)
app.include_router(analytics_router)


@app.get("/")
def root():
    return {"message": f"{settings.APP_NAME} is running"}


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": settings.APP_NAME
    }