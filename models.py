from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import relationship

from .database import Base


class Account(Base):
    __tablename__ = "accounts"

    account_id = Column(Integer, primary_key=True, autoincrement="auto")
    email = Column(String, unique=True, index=True)
    account_name = Column(String)
    app_secret_token = Column(String, default=None)
    website = Column(String, default=None)

    destinations = relationship("Destination", back_populates="account")


class Destination(Base):
    __tablename__ = "destinations"

    id = Column(Integer, primary_key=True, autoincrement="auto")
    url = Column(String)
    http_method = Column(String)
    headers = Column(JSON)
    account_id = Column(Integer, ForeignKey("accounts.account_id"))

    account = relationship("Account", back_populates="destinations", cascade="all,delete", passive_deletes=True)