from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.trade_order import TradeOrder
from app.models.product import Product
from app.models.shipment import Shipment
from app.models.user import User
from app.schemas.analytics import (
    OrdersByStatusResponse,
    TopProductsResponse,
    ShipmentSummaryResponse,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/orders-by-status", response_model=list[OrdersByStatusResponse])
def orders_by_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    results = (
        db.query(
            TradeOrder.order_status,
            func.count(TradeOrder.id).label("count"),
        )
        .group_by(TradeOrder.order_status)
        .all()
    )

    return [
        OrdersByStatusResponse(order_status=row.order_status, count=row.count)
        for row in results
    ]


@router.get("/top-products", response_model=list[TopProductsResponse])
def top_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    results = (
        db.query(
            TradeOrder.product_id,
            Product.product_name,
            func.sum(TradeOrder.quantity).label("total_quantity"),
        )
        .join(Product, TradeOrder.product_id == Product.id)
        .group_by(TradeOrder.product_id, Product.product_name)
        .order_by(func.sum(TradeOrder.quantity).desc())
        .all()
    )

    return [
        TopProductsResponse(
            product_id=row.product_id,
            product_name=row.product_name,
            total_quantity=row.total_quantity,
        )
        for row in results
    ]


@router.get("/shipment-summary", response_model=list[ShipmentSummaryResponse])
def shipment_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    results = (
        db.query(
            Shipment.shipment_status,
            func.count(Shipment.id).label("count"),
        )
        .group_by(Shipment.shipment_status)
        .all()
    )

    return [
        ShipmentSummaryResponse(shipment_status=row.shipment_status, count=row.count)
        for row in results
    ]