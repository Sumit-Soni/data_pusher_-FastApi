from typing import Union, Dict

from pydantic import BaseModel


class DestinationBase(BaseModel):
    url: str
    http_method: str
    headers: dict


class Destination(DestinationBase):
    id: int
    account_id: int

    class Config:
        orm_mode = True


class AccountBase(BaseModel):
    email: str
    account_name: str
    website: str

class AccountCreate(AccountBase):
    app_secret_token: str

class Account(AccountBase):
    account_id: int
    destinations: list[Destination] = []

    class Config:
        orm_mode = True