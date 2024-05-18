import pytest

from src.db import services
from src.schemas import admins, users


@pytest.mark.asyncio
async def test_create_get_user(CreateUser_data, db) -> None:
    created_user = await services.create_user(CreateUser_data, db)
    assert created_user.txid == CreateUser_data.txid


@pytest.mark.asyncio
async def test_activate_license(CreateUser_data, db):
    license = users.License(license=CreateUser_data.License_Key)
    End_Date, product = await services.activate_license(license, db)
    assert CreateUser_data.End_Date == End_Date
    assert CreateUser_data.product == product
    get_user = await services.get_user(txid=CreateUser_data.txid, db=db)
    assert get_user.License_Activated is True


@pytest.mark.asyncio
async def test_add_user(CreateUser_data, db):
    result = await services.add_user(CreateUser_data, db)
    # becuase we have already created a user in database it should return user already exists
    assert result == {"Error": "The orderID already Exists!"}


@pytest.mark.asyncio
async def test_update_user(CreateUser_data, EditUser_data, db):
    user = await services.get_user(CreateUser_data.txid, db)
    result = await services.update_user(user, EditUser_data, db=db)
    assert result.product == users.Product.ProductB
    assert result.email_id == "testing_new123@gmail.com"
    assert result.contact_no == "111111111"


@pytest.mark.asyncio
async def test_reset_licence_activated(CreateUser_data, db):
    user = await services.get_user(CreateUser_data.txid, db)
    user = await services.reset_licence_activated(user, db)
    assert user.License_Activated is False


@pytest.mark.asyncio
async def test_db_delete_user(CreateUser_data, db):
    user = await services.get_user(CreateUser_data.txid, db)
    await services.delete_user(user, db=db)
    assert await services.get_user(CreateUser_data.txid, db) is None


@pytest.mark.asyncio
async def test_create_admin(admin_data, db):
    admin = await services.create_admin(admin_data, db)
    assert admin.username == admin_data.username


@pytest.mark.asyncio
async def test_get_admin(admin_data, db):
    admin = await services.get_admin(admin_data.username, db)
    admin = admins.AdminInDB.model_validate(admin)
    assert admin.username == admin_data.username
    assert admin.scope == admin_data.scope


@pytest.mark.asyncio
async def test_delete_admin(admin_data, db):
    result = await services.delete_admin(admin_data.username, db)
    assert result == {"Success": f"Admin with username {admin_data.username} deleted!"}
