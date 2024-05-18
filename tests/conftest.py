import datetime
import random
import string

import pytest
from dateutil.relativedelta import relativedelta
from fastapi.testclient import TestClient

from src.db import database
from src.main import app
from src.schemas import admins, users
from src.security.license import LicenseGen
from src.settings import SUPERUSER_LOGIN, SUPERUSER_PASSWORD

client = TestClient(app)


@pytest.fixture(scope="session")
def db():
    return database.SessionLocal()


@pytest.fixture(scope="session")
def admin_data():
    return admins.CreateAdmin(
        username="testing",
        scope=admins.Scopes.admin,
        password="testing",
    )


@pytest.fixture(scope="session")
def CreateUser_data():
    license = LicenseGen()
    TxID = "".join(random.choices(string.ascii_letters + string.digits, k=16))
    test_user = users.CreateUser(
        txid=TxID,
        amount=1111,
        payment_method="NA",
        product=users.Product.ProductA,
        email_id="testing@gmail.com",
        contact_no="9999999999",
        subscription=12,
        order_date=datetime.datetime.now(datetime.UTC),
        License_Key=license.create(TxID + "testing@gmail.com"),
        License_Activated=False,
        Start_Date=datetime.date.today(),  # add the actual order date
        End_Date=datetime.date.today() + relativedelta(months=12),
    )
    return test_user


@pytest.fixture(scope="session")
def AddUser_data():
    TxID = "".join(random.choices(string.ascii_letters + string.digits, k=16))
    Email = (
        "".join(random.choices(string.ascii_letters + string.digits, k=5))
        + "@testing.com"
    )
    test_user = users.AddUser(
        txid=TxID,
        amount=1111,
        product=users.Product.ProductA,
        email_id=Email,
        contact_no="9999999999",
        subscription=12,
        order_date=datetime.datetime.now(datetime.UTC),
    )
    return test_user


@pytest.fixture(scope="session")
def EditUser_data():
    edit_user = users.EditUser(
        product=users.Product.ProductB,
        email_id="testing_new123@gmail.com",
        contact_no="111111111",
    )
    return edit_user


@pytest.fixture(scope="session")
def login_credentials():
    return {
        "username": SUPERUSER_LOGIN,
        "password": SUPERUSER_PASSWORD,
        "scope": "admin",
    }


@pytest.fixture(scope="session")
def login(login_credentials):
    response = client.post("/login", data=login_credentials)
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert token is not None
    return token
