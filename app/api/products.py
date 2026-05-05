from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin_or_operations
from app.core.database import get_db
from app.models.product import Product
from app.models.supplier import Supplier
from app.models.user import User
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/", response_model=ProductResponse)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_operations),
):
    existing_product = db.query(Product).filter(Product.sku == product_data.sku).first()
    if existing_product:
        raise HTTPException(status_code=400, detail="Product SKU already exists")

    supplier = db.query(Supplier).filter(Supplier.id == product_data.supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    new_product = Product(
        sku=product_data.sku,
        product_name=product_data.product_name,
        category=product_data.category,
        unit_price=product_data.unit_price,
        currency=product_data.currency,
        supplier_id=product_data.supplier_id,
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


@router.get("/", response_model=list[ProductResponse])
def list_products(
    category: str | None = None,
    supplier_id: int | None = None,
    skip: int = 0,
    limit: int = 10,
    sort_by: str = "id",
    sort_order: str = "asc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Product)

    if category:
        query = query.filter(Product.category == category)

    if supplier_id:
        query = query.filter(Product.supplier_id == supplier_id)

    if sort_by == "product_name":
        sort_column = Product.product_name
    elif sort_by == "unit_price":
        sort_column = Product.unit_price
    elif sort_by == "created_at":
        sort_column = Product.created_at
    else:
        sort_column = Product.id

    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    products = query.offset(skip).limit(limit).all()
    return products


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_operations),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    existing_product = (
        db.query(Product)
        .filter(Product.sku == product_data.sku, Product.id != product_id)
        .first()
    )
    if existing_product:
        raise HTTPException(status_code=400, detail="Product SKU already exists")

    supplier = db.query(Supplier).filter(Supplier.id == product_data.supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    product.sku = product_data.sku
    product.product_name = product_data.product_name
    product.category = product_data.category
    product.unit_price = product_data.unit_price
    product.currency = product_data.currency
    product.supplier_id = product_data.supplier_id

    db.commit()
    db.refresh(product)

    return product