from datetime import datetime
from pydantic import BaseModel, EmailStr


class SupplierCreate(BaseModel):
    company_name: str
    contact_name: str
    email: EmailStr
    country: str


class SupplierUpdate(BaseModel):
    company_name: str
    contact_name: str
    email: EmailStr
    country: str


class SupplierResponse(BaseModel):
    id: int
    company_name: str
    contact_name: str
    email: EmailStr
    country: str
    created_at: datetime

    class Config:
        from_attributes = True