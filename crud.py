import secrets
from sqlalchemy.orm import Session
from . import models, schemas


def get_account(db: Session, account_id: int):
    return db.query(models.Account).filter(models.Account.account_id == account_id).first()


def get_account_by_email(db: Session, email: str):
    return db.query(models.Account).filter(models.Account.email == email).first()


def get_accounts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Account).offset(skip).limit(limit).all()


def create_account(db: Session, account: schemas.AccountCreate):
    app_secret_token = secrets.token_hex(16)
    account_dict = account.model_dump()
    del account_dict["app_secret_token"]
    db_user = models.Account(**account_dict, app_secret_token = app_secret_token)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_destinations(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Destination).offset(skip).limit(limit).all()


def create_account_destination(db: Session, destination: schemas.Destination, account_id: int):
    destination_dict = destination.model_dump()
    del destination_dict['account_id']
    del destination_dict['id']
    db_item = models.Destination(**destination_dict, account_id = account_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item