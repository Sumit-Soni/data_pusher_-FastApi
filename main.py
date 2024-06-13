from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
import requests

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/accounts/", response_model=schemas.Account)
def create_account(account: schemas.AccountCreate, db: Session = Depends(get_db)):
    db_account = crud.get_account_by_email(db, email=account.email)
    if db_account:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_account(db=db, account=account)


@app.get("/accounts/", response_model=list[schemas.Account])
def read_accounts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    accounts = crud.get_accounts(db, skip=skip, limit=limit)
    return accounts


@app.get("/accounts/{account_id}")
def read_account(account_id: int, db: Session = Depends(get_db)):
    db_account = crud.get_account(db, account_id=account_id)
    if db_account is None:
        raise HTTPException(status_code=404, detail="account not found")
    return {"data": db_account}


@app.delete("/accounts/{account_id}")
def delete_account(account_id: int, db: Session = Depends(get_db)):
    db_account = crud.get_account(db, account_id=account_id)
    if db_account is None:
        raise HTTPException(status_code=404, detail="account not found")
    db.delete(db_account)
    db.commit()
    return {"action": "Delete", "data": db_account}


@app.post("/accounts/{account_id}/destinations/", response_model=schemas.Destination)
def create_destination_for_account(
    account_id: int, destination: schemas.Destination, db: Session = Depends(get_db)
):
    return crud.create_account_destination(db=db, destination=destination, account_id=account_id)


@app.get("/destinations/", response_model=list[schemas.Destination])
def read_destinations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_destinations(db, skip=skip, limit=limit)
    return items


@app.get("/accounts/destinations/{account_id}", response_model=list[schemas.Destination])
def get_destinations_for_account(
    account_id: int, db: Session = Depends(get_db)
):
    return db.query(models.Destination).filter(models.Destination.account_id == account_id).all()


@app.post("/server/incoming_data")
def push_recieves_data(
    data: dict, db: Session = Depends(get_db)
):
    try:
        token = data["app_secret_token"]
        if not token:
            return {
                "error" : "Invalid Data"
            }
    except:
        return {
            "error" : "Invalid Data"
        }
    db_account = db.query(models.Account).filter(models.Account.app_secret_token == token).first()
    if not db_account:
        return {
            "error": "Un Authenticate"
        }
    
    account_id = db_account.account_id
    destinations = db.query(models.Destination).filter(models.Destination.account_id == account_id).all()
    for destination in destinations:
        if destination.http_method == "GET":
            try:
                code = requests.get(destination.url, params=data)
                return {"Success" : code.status_code}
            except Exception as e:
                return {
                    "error" : str(e)
                }
        if destination.http_method == "POST":
            try:
                code = requests.post(destination.url, json=data)
                return {"Success" : code.status_code}
            except Exception as e:
                return {
                    "error" : str(e)
                }