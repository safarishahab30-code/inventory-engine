from fastapi import FastAPI
from schemas import ProductCreate, ProductResponse, ProductUpdate

app = FastAPI(title="Inventory Engine API", version="1.0.0")

@app.get("/")
def read_root():
    return {"message": "خوش آمدید! سیستم انبارداری آنلاین فعال است."}
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from inventory_core.database import get_db
from inventory_core.models.product import Product

app = FastAPI(title="Inventory Engine API", version="1.0.0")

@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return {"status": "success", "count": len(products), "data": products}
from typing import List

@app.get("/products", response_model=List[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

@app.post("/products", response_model=ProductResponse, status_code=210)  # یا status_code=201
def create_product(product_in: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(**product_in.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product
from fastapi import HTTPException, status

@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product
from schemas import ProductUpdate

@app.put("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product_in: ProductUpdate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = product_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product
@app.put("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product_in: ProductUpdate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    update_data = product_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product
@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    db.delete(product)
    db.commit()
    return None
