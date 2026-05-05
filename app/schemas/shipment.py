from datetime import datetime
from pydantic import BaseModel


class ShipmentCreate(BaseModel):
    order_id: int
    carrier: str
    tracking_number: str


class ShipmentUpdate(BaseModel):
    carrier: str
    tracking_number: str
    shipment_status: str
    shipped_at: datetime | None = None
    delivered_at: datetime | None = None


class ShipmentResponse(BaseModel):
    id: int
    order_id: int
    carrier: str
    tracking_number: str
    shipment_status: str
    shipped_at: datetime | None
    delivered_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True