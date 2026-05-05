from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin_or_operations
from app.core.database import get_db
from app.models.supplier import Supplier
from app.models.user import User
from app.schemas.supplier import SupplierCreate, SupplierUpdate, SupplierResponse

router = APIRouter(prefix="/suppliers", tags=["suppliers"])


@router.post("/", response_model=SupplierResponse)
def create_supplier(
    supplier_data: SupplierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_operations),
):
    existing_supplier = db.query(Supplier).filter(Supplier.email == supplier_data.email).first()
    if existing_supplier:
        raise HTTPException(status_code=400, detail="Supplier email already registered")

    new_supplier = Supplier(
        company_name=supplier_data.company_name,
        contact_name=supplier_data.contact_name,
        email=supplier_data.email,
        country=supplier_data.country,
    )

    db.add(new_supplier)
    db.commit()
    db.refresh(new_supplier)

    return new_supplier


@router.get("/", response_model=list[SupplierResponse])
def list_suppliers(
    country: str | None = None,
    skip: int = 0,
    limit: int = 10,
    sort_by: str = "id",
    sort_order: str = "asc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Supplier)

    if country:
        query = query.filter(Supplier.country == country)

    if sort_by == "company_name":
        sort_column = Supplier.company_name
    elif sort_by == "created_at":
        sort_column = Supplier.created_at
    else:
        sort_column = Supplier.id

    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    suppliers = query.offset(skip).limit(limit).all()
    return suppliers


@router.get("/{supplier_id}", response_model=SupplierResponse)
def get_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    return supplier


@router.put("/{supplier_id}", response_model=SupplierResponse)
def update_supplier(
    supplier_id: int,
    supplier_data: SupplierUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_operations),
):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    existing_supplier = (
        db.query(Supplier)
        .filter(Supplier.email == supplier_data.email, Supplier.id != supplier_id)
        .first()
    )
    if existing_supplier:
        raise HTTPException(status_code=400, detail="Supplier email already registered")

    supplier.company_name = supplier_data.company_name
    supplier.contact_name = supplier_data.contact_name
    supplier.email = supplier_data.email
    supplier.country = supplier_data.country

    db.commit()
    db.refresh(supplier)

    return supplier