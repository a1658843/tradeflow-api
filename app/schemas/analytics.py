from pydantic import BaseModel


class OrdersByStatusResponse(BaseModel):
    order_status: str
    count: int


class TopProductsResponse(BaseModel):
    product_id: int
    product_name: str
    total_quantity: int


class ShipmentSummaryResponse(BaseModel):
    shipment_status: str
    count: int