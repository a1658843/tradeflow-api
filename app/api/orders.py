from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin_or_operations
from app.core.database import get_db
from app.models.trade_order import TradeOrder
from app.models.customer import Customer
from app.models.product import Product
from app.models.user import User
from app.schemas.trade_order import (
    TradeOrderCreate,
    TradeOrderUpdate,
    TradeOrderResponse,
)

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=TradeOrderResponse)
def create_order(
    order_data: TradeOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_operations),
):
    customer = db.query(Customer).filter(Customer.id == order_data.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    product = db.query(Product).filter(Product.id == order_data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if order_data.created_by is not None:
        user = db.query(User).filter(User.id == order_data.created_by).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

    if (
        order_data.expected_ship_date is not None
        and order_data.expected_delivery_date is not None
        and order_data.expected_delivery_date < order_data.expected_ship_date
    ):
        raise HTTPException(
            status_code=400,
            detail="Expected delivery date cannot be earlier than expected ship date",
        )

    unit_price = product.unit_price
    total_amount = order_data.quantity * unit_price

    new_order = TradeOrder(
        customer_id=order_data.customer_id,
        product_id=order_data.product_id,
        quantity=order_data.quantity,
        unit_price=unit_price,
        total_amount=total_amount,
        currency=order_data.currency,
        order_status="draft",
        shipment_status="pending",
        created_by=order_data.created_by,
        expected_ship_date=order_data.expected_ship_date,
        expected_delivery_date=order_data.expected_delivery_date,
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return new_order


@router.get("/", response_model=list[TradeOrderResponse])
def list_orders(
    customer_id: int | None = None,
    product_id: int | None = None,
    order_status: str | None = None,
    shipment_status: str | None = None,
    skip: int = 0,
    limit: int = 10,
    sort_by: str = "id",
    sort_order: str = "asc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(TradeOrder)

    if customer_id:
        query = query.filter(TradeOrder.customer_id == customer_id)

    if product_id:
        query = query.filter(TradeOrder.product_id == product_id)

    if order_status:
        query = query.filter(TradeOrder.order_status == order_status)

    if shipment_status:
        query = query.filter(TradeOrder.shipment_status == shipment_status)

    if sort_by == "total_amount":
        sort_column = TradeOrder.total_amount
    elif sort_by == "created_at":
        sort_column = TradeOrder.created_at
    else:
        sort_column = TradeOrder.id

    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    orders = query.offset(skip).limit(limit).all()
    return orders


@router.get("/{order_id}", response_model=TradeOrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = db.query(TradeOrder).filter(TradeOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order


@router.put("/{order_id}", response_model=TradeOrderResponse)
def update_order(
    order_id: int,
    order_data: TradeOrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_operations),
):
    order = db.query(TradeOrder).filter(TradeOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    customer = db.query(Customer).filter(Customer.id == order_data.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    product = db.query(Product).filter(Product.id == order_data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if order_data.created_by is not None:
        user = db.query(User).filter(User.id == order_data.created_by).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

    if (
        order_data.expected_ship_date is not None
        and order_data.expected_delivery_date is not None
        and order_data.expected_delivery_date < order_data.expected_ship_date
    ):
        raise HTTPException(
            status_code=400,
            detail="Expected delivery date cannot be earlier than expected ship date",
        )

    unit_price = product.unit_price
    total_amount = order_data.quantity * unit_price

    order.customer_id = order_data.customer_id
    order.product_id = order_data.product_id
    order.quantity = order_data.quantity
    order.unit_price = unit_price
    order.total_amount = total_amount
    order.currency = order_data.currency
    order.order_status = order_data.order_status
    order.shipment_status = order_data.shipment_status
    order.created_by = order_data.created_by
    order.expected_ship_date = order_data.expected_ship_date
    order.expected_delivery_date = order_data.expected_delivery_date
    order.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(order)

    return order