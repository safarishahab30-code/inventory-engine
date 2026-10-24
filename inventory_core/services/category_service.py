from sqlalchemy.orm import Session
from inventory_core.models.category import Category


def create_category(db: Session, name: str, user_role: str):
  if user_role != "admin":
    raise PermissionError(
        "فقط مدیر (Admin) اجازه تعریف دسته‌بندی جدید را دارد."
    )

  existing = db.query(Category).filter_by(name=name).first()
  if existing:
    raise ValueError("این دسته‌بندی از قبل وجود دارد.")

  new_cat = Category(name=name)
  db.add(new_cat)
  db.commit()
  db.refresh(new_cat)
  return new_cat


def get_all_categories(db: Session):
  return db.query(Category).all()
