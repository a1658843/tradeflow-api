from datetime import datetime
from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    sku: str
    product_name: str
    category: str
    unit_price: float = Field(gt=0)
    currency: str = "USD"
    supplier_id: int


class ProductUpdate(BaseModel):
    sku: str
    product_name: str
    category: str
    unit_price: float = Field(gt=0)
    currency: str
    supplier_id: int


class ProductResponse(BaseModel):
    id: int
    sku: str
    product_name: str
    category: str
    unit_price: float
    currency: str
    supplier_id: int
    created_at: datetime

    class Config:
        from_attributes = True