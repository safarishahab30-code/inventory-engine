from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from inventory_core.database import get_db
from inventory_core.models.user import User
from inventory_core.auth import authenticate_user, create_access_token, get_current_user

from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from inventory_core.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
)


from inventory_core.database import get_db
from inventory_core.models.product import Product
from inventory_core.models.stock_movement import StockMovement
from inventory_core.schemas import (
    MovementType,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
    StockMovementCreate,
)

from fastapi import APIRouter

router = APIRouter()

app = FastAPI(
    title="Inventory Engine API",
    version="1.0.0",
)


@app.get("/")
def read_root():
    return {
        "message": "سیستم انبارداری آنلاین فعال است."
    }


@app.get(
    "/products",
    response_model=List[ProductResponse],
)
def get_products(
    db: Session = Depends(get_db),
):
    return db.query(Product).all()


@app.post(
    "/products",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
):
    existing_product = (
        db.query(Product)
        .filter(Product.name == product_data.name)
        .first()
    )

    if existing_product is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="محصولی با این نام قبلاً ثبت شده است.",
        )

    new_product = Product(
        **product_data.model_dump()
    )

    try:
        db.add(new_product)
        db.commit()
        db.refresh(new_product)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="اطلاعات محصول تکراری یا نامعتبر است.",
        )

    return new_product


@app.get(
    "/products/{product_id}",
    response_model=ProductResponse,
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="محصول یافت نشد.",
        )

    return product


@app.put(
    "/products/{product_id}",
    response_model=ProductResponse,
)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
):
    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="محصول یافت نشد.",
        )

    update_data = product_data.model_dump(
        exclude_unset=True
    )

    if "name" in update_data:
        duplicate_product = (
            db.query(Product)
            .filter(
                Product.name == update_data["name"],
                Product.id != product_id,
            )
            .first()
        )

        if duplicate_product is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="محصولی با این نام قبلاً ثبت شده است.",
            )

    for field, value in update_data.items():
        setattr(product, field, value)

    try:
        db.commit()
        db.refresh(product)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="اطلاعات محصول نامعتبر است.",
        )

    return product


@app.delete(
    "/products/{product_id}",
)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="محصول یافت نشد.",
        )

    try:
        db.delete(product)
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="این محصول دارای تراکنش است و قابل حذف نیست.",
        )

    return {
        "message": "محصول با موفقیت حذف شد."
    }


@app.post(
    "/transactions",
    status_code=status.HTTP_201_CREATED,
)
def create_stock_movement(
    movement: StockMovementCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    product = (
        db.query(Product)
        .filter(Product.id == movement.product_id)
        .first()
    )

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="محصول یافت نشد.",
        )

    if movement.quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="تعداد باید بیشتر از صفر باشد.",
        )

    if movement.movement_type == MovementType.OUT:
        if product.quantity < movement.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="موجودی انبار کافی نیست.",
            )

        product.quantity -= movement.quantity

    elif movement.movement_type == MovementType.IN:
        product.quantity += movement.quantity

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="نوع تراکنش نامعتبر است.",
        )

    new_transaction = StockMovement(
        product_id=movement.product_id,
        quantity=movement.quantity,
        movement_type=movement.movement_type,
        notes=movement.notes,
        user_id=current_user.id,
    )

    try:
        db.add(new_transaction)
        db.commit()
        db.refresh(new_transaction)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ثبت تراکنش امکان‌پذیر نیست.",
        )

    return {
        "message": "تراکنش با موفقیت ثبت شد.",
        "product_id": product.id,
        "new_stock": product.quantity,
        "transaction_id": new_transaction.id,
    }
@app.get("/inventory/report")
def get_inventory_report(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    total_items = sum(p.quantity for p in products)
    total_value = sum(p.quantity * p.selling_price for p in products)
    return {
        "total_products": len(products),
        "total_quantity": total_items,
        "total_inventory_value": total_value,
        "products": products
    }

@app.get("/reorders")
def get_reorder_items(db: Session = Depends(get_db)):
    # اقلامی که موجودی‌شان کمتر یا مساوی حداقل موجودی (min_stock) است
    reorder_list = db.query(Product).filter(Product.quantity <= Product.min_stock).all()
    return reorder_list
import csv
import io
from fastapi import Response

def generate_csv_response(headers: list, rows: list, filename: str = "report.csv"):
    output = io.StringIO()
    # افزودن BOM برای خوانایی صحیح حروف فارسی در اکسل
    output.write('\ufeff')
    
    writer = csv.writer(output)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
        
    return Response(
        content=output.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
@router.get("/reports/inventory")
def inventory_report(format: str = "json", db: Session = Depends(get_db)):
    data = get_inventory_valuation(db)
    
    if format == "csv":
        headers = ["شناسه کالا", "SKU", "نام کالا", "موجودی کل", "ارزش کل (تومان)"]
        rows = [[item.id, item.sku, item.name, item.total_on_hand, item.total_value] for item in data]
        return generate_csv_response(headers, rows, "inventory_report.csv")
        
    return {"items": data}
@app.post("/token", operation_id="obtain_user_access_token")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="نام کاربری یا رمز عبور اشتباه است",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}
import logging

# تنظیمات پایه لاگ‌گیری
logging.basicConfig(
    filename="inventory.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8",
)
logger = logging.getLogger("inventory_api")
import time
from fastapi import Request


@app.middleware("http")
async def log_requests(request: Request, call_next):
  start_time = time.time()
  response = await call_next(request)
  process_time = time.time() - start_time
  logger.info(
      f"Path: {request.url.path} | Method: {request.method} | Status:"
      f" {response.status_code} | Duration: {process_time:.4f}s"
  )
  return response
import csv
from fastapi.responses import StreamingResponse
import io


@app.get("/reports/inventory/csv")
def export_inventory_csv(db: Session = Depends(get_db)):
  output = io.StringIO()
  writer = csv.writer(output)
  writer.writerow(["ID", "Product Name", "Quantity", "Price"])

  # فرض بر این است که مدل Product را داری
  products = db.query(Product).all()
  for p in products:
    writer.writerow([p.id, p.name, p.quantity, p.price])

  output.seek(0)
  return StreamingResponse(
      iter([output.getvalue()]),
      media_type="text/csv",
      headers={
          "Content-Disposition": "attachment; filename=inventory_report.csv"
      },
  )
from fastapi.security import OAuth2PasswordRequestForm
from inventory_core.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_password_hash,
)
from inventory_core.models.user import User

@app.post("/register")
def register_user(username: str, password: str, db: Session = Depends(get_db)):
    existing = get_user_by_username(db, username)
    if existing:
        raise HTTPException(status_code=400, detail="این نام کاربری قبلاً ثبت شده است")
    
    hashed_pwd = get_password_hash(password)
    new_user = User(username=username, hashed_password=hashed_pwd)
    db.add(new_user)
    db.commit()
    return {"message": "کاربر با موفقیت ثبت‌نام شد"}

@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="نام کاربری یا رمز عبور اشتباه است",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
