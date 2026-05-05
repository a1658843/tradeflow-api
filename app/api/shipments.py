from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin_or_operations
from app.core.database import get_db
from app.models.shipment import Shipment
from app.models.trade_order import TradeOrder
from app.models.user import User
from app.schemas.shipment import ShipmentCreate, ShipmentUpdate, ShipmentResponse

router = APIRouter(prefix="/shipments", tags=["shipments"])


@router.post("/", response_model=ShipmentResponse)
def create_shipment(
    shipment_data: ShipmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_operations),
):
    order = db.query(TradeOrder).filter(TradeOrder.id == shipment_data.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.order_status == "cancelled":
        raise HTTPException(status_code=400, detail="Cancelled orders cannot be shipped")

    existing_shipment_for_order = (
        db.query(Shipment).filter(Shipment.order_id == shipment_data.order_id).first()
    )
    if existing_shipment_for_order:
        raise HTTPException(status_code=400, detail="Shipment already exists for this order")

    existing_tracking = (
        db.query(Shipment)
        .filter(Shipment.tracking_number == shipment_data.tracking_number)
        .first()
    )
    if existing_tracking:
        raise HTTPException(status_code=400, detail="Tracking number already exists")

    new_shipment = Shipment(
        order_id=shipment_data.order_id,
        carrier=shipment_data.carrier,
        tracking_number=shipment_data.tracking_number,
        shipment_status="pending",
    )

    db.add(new_shipment)

    order.shipment_status = "pending"

    db.commit()
    db.refresh(new_shipment)

    return new_shipment


@router.get("/", response_model=list[ShipmentResponse])
def list_shipments(
    order_id: int | None = None,
    shipment_status: str | None = None,
    skip: int = 0,
    limit: int = 10,
    sort_by: str = "id",
    sort_order: str = "asc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Shipment)

    if order_id:
        query = query.filter(Shipment.order_id == order_id)

    if shipment_status:
        query = query.filter(Shipment.shipment_status == shipment_status)

    if sort_by == "created_at":
        sort_column = Shipment.created_at
    else:
        sort_column = Shipment.id

    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    shipments = query.offset(skip).limit(limit).all()
    return shipments


@router.get("/{shipment_id}", response_model=ShipmentResponse)
def get_shipment(
    shipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    return shipment


@router.put("/{shipment_id}", response_model=ShipmentResponse)
def update_shipment(
    shipment_id: int,
    shipment_data: ShipmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_operations),
):
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    order = db.query(TradeOrder).filter(TradeOrder.id == shipment.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Related order not found")

    existing_tracking = (
        db.query(Shipment)
        .filter(
            Shipment.tracking_number == shipment_data.tracking_number,
            Shipment.id != shipment_id,
        )
        .first()
    )
    if existing_tracking:
        raise HTTPException(status_code=400, detail="Tracking number already exists")

    if shipment.shipment_status == "delivered" and shipment_data.shipment_status != "delivered":
        raise HTTPException(
            status_code=400,
            detail="Delivered shipment cannot be changed to another status",
        )

    if shipment_data.shipment_status == "delivered" and shipment_data.delivered_at is None:
        raise HTTPException(
            status_code=400,
            detail="Delivered shipment must include delivered_at",
        )

    shipment.carrier = shipment_data.carrier
    shipment.tracking_number = shipment_data.tracking_number
    shipment.shipment_status = shipment_data.shipment_status
    shipment.shipped_at = shipment_data.shipped_at
    shipment.delivered_at = shipment_data.delivered_at

    order.shipment_status = shipment_data.shipment_status

    db.commit()
    db.refresh(shipment)

    return shipment