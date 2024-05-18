from sqlalchemy import DATE, FLOAT, Boolean, Column, DateTime, Enum, Integer, String

from src.db.database import Base
from src.schemas import admins


# Refer to README.md for more details
class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    txid = Column(String, unique=True)
    amount = Column(FLOAT)
    payment_method = Column(String)
    product = Column(String)
    email_id = Column(String)
    contact_no = Column(String)
    subscription = Column(Integer)
    order_date = Column(DateTime)
    Start_Date = Column(DATE)
    End_Date = Column(DATE)
    License_Key = Column(String, unique=True)
    License_Activated = Column(Boolean)


class Admins(Base):
    __tablename__ = "admins"

    username = Column(String, primary_key=True, index=True)
    disabled = Column(Boolean, default=False)
    scope = Column(Enum(admins.Scopes), default=None)
    hashed_password = Column(String)
