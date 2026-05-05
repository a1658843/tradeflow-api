from datetime import datetime
from pydantic import BaseModel, Field


class TradeOrderCreate(BaseModel):
    customer_id: int
    product_id: int
    quantity: int = Field(gt=0)
    currency: str = "USD"
    created_by: int | None = None
    expected_ship_date: datetime | None = None
    expected_delivery_date: datetime | None = None


class TradeOrderUpdate(BaseModel):
    customer_id: int
    product_id: int
    quantity: int = Field(gt=0)
    currency: str
    order_status: str
    shipment_status: str
    created_by: int | None = None
    expected_ship_date: datetime | None = None
    expected_delivery_date: datetime | None = None


class TradeOrderResponse(BaseModel):
    id: int
    customer_id: int
    product_id: int
    quantity: int
    unit_price: float
    total_amount: float
    currency: str
    order_status: str
    shipment_status: str
    created_by: int | None
    expected_ship_date: datetime | None
    expected_delivery_date: datetime | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True