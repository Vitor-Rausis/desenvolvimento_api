from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from typing import List, Optional
from models import User, DataItem, UserCreate, UserUpdate, DataItemCreate, DataItemUpdate
from auth import get_password_hash

def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username, 
        email=user.email, 
        hashed_password=hashed_password,
        user_type=user.user_type
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Usuário já existe")

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()

def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
   
    update_data = user_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(db_user, key):
            setattr(db_user, key, value)
    
    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Dados inválidos para atualização")

def delete_user(db: Session, user_id: int) -> bool:
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False

    db.delete(db_user)
    db.commit()
    return True

def create_data_item(db: Session, data_item: DataItemCreate) -> DataItem:
    db_data_item = DataItem(
        name=data_item.name,
        description=data_item.description,
        user_id=data_item.user_id
    )

    db.add(db_data_item)
    db.commit()
    db.refresh(db_data_item)
    return db_data_item

def get_data_item(db: Session, item_id: str) -> Optional[DataItem]:
    return db.query(DataItem).filter(DataItem.id == item_id).first()

def get_data_items_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[DataItem]:
    return db.query(DataItem).filter(DataItem.user_id == user_id).offset(skip).limit(limit).all()

def get_all_data_items(db: Session, skip: int = 0, limit: int = 100) -> List[DataItem]:
    return db.query(DataItem).offset(skip).limit(limit).all()

def update_data_item(db: Session, item_id: str, data_item: DataItemUpdate) -> Optional[DataItem]:
    db_data_item = get_data_item(db, item_id)
    if not db_data_item:
        return None

    update_data = data_item.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_data_item, key, value)

    db.commit()
    db.refresh(db_data_item)
    return db_data_item

def delete_data_item(db: Session, item_id: str) -> bool:
    db_data_item = get_data_item(db, item_id)
    if not db_data_item:
        return False

    db.delete(db_data_item)
    db.commit()
    return True

def can_access_data_item(db: Session, item_id: str, user_id: int, user_type: str) -> bool:
    if user_type == "admin":
        return True
    
    db_data_item = get_data_item(db, item_id)
    if not db_data_item:
        return False
    
    return db_data_item.user_id == user_id

