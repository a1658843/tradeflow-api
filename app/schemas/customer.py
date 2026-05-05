from datetime import datetime
from pydantic import BaseModel, EmailStr


class CustomerCreate(BaseModel):
    company_name: str
    contact_name: str
    email: EmailStr
    country: str


class CustomerUpdate(BaseModel):
    company_name: str
    contact_name: str
    email: EmailStr
    country: str


class CustomerResponse(BaseModel):
    id: int
    company_name: str
    contact_name: str
    email: EmailStr
    country: str
    created_at: datetime

    class Config:
        from_attributes = True