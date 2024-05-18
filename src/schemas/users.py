import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr


# You can replace these with the actual products
class Product(str, Enum):
    ProductA = "Product A"
    ProductB = "Product B"

    # used for input, output, type conversions and validation


class BaseUser(BaseModel):
    txid: str
    amount: float
    payment_method: str
    product: str
    email_id: str
    contact_no: str
    subscription: int
    order_date: datetime.datetime
    Start_Date: datetime.date
    End_Date: datetime.date
    License_Key: str
    License_Activated: bool


class User(BaseUser):
    model_config = ConfigDict(from_attributes=True)


# Just for naming
class CreateUser(BaseUser):
    pass


class License(BaseModel):
    license: str


# used for adding a new user
class AddUser(BaseModel):
    txid: str
    amount: float
    product: str
    email_id: EmailStr
    contact_no: str
    order_date: datetime.datetime  # when adding user manually it also gives datetime
    subscription: int


# # used for editing the user data
class EditUser(BaseModel):
    product: str
    email_id: EmailStr
    contact_no: str


class Email(BaseModel):
    email: str
    tx_id: str
    skip: bool
    replace: bool


class SkipReplaceUser(BaseModel):
    emails: list[Email]
    file_name: str
