from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin_or_operations
from app.core.database import get_db
from app.models.customer import Customer
from app.models.user import User
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("/", response_model=CustomerResponse)
def create_customer(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_operations),
):
    existing_customer = db.query(Customer).filter(Customer.email == customer_data.email).first()
    if existing_customer:
        raise HTTPException(status_code=400, detail="Customer email already registered")

    new_customer = Customer(
        company_name=customer_data.company_name,
        contact_name=customer_data.contact_name,
        email=customer_data.email,
        country=customer_data.country,
    )

    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    return new_customer


@router.get("/", response_model=list[CustomerResponse])
def list_customers(
    country: str | None = None,
    skip: int = 0,
    limit: int = 10,
    sort_by: str = "id",
    sort_order: str = "asc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Customer)

    if country:
        query = query.filter(Customer.country == country)

    if sort_by == "company_name":
        sort_column = Customer.company_name
    elif sort_by == "created_at":
        sort_column = Customer.created_at
    else:
        sort_column = Customer.id

    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    customers = query.offset(skip).limit(limit).all()
    return customers


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return customer


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_operations),
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    existing_customer = (
        db.query(Customer)
        .filter(Customer.email == customer_data.email, Customer.id != customer_id)
        .first()
    )
    if existing_customer:
        raise HTTPException(status_code=400, detail="Customer email already registered")

    customer.company_name = customer_data.company_name
    customer.contact_name = customer_data.contact_name
    customer.email = customer_data.email
    customer.country = customer_data.country

    db.commit()
    db.refresh(customer)

    return customer