import httpx
import pytest

from src.db import services
from src.main import app
from src.schemas.users import Product

app = httpx.ASGITransport(app=app)


@pytest.mark.asyncio(scope="session")
async def test_add_user(AddUser_data, login, db) -> None:
    async with httpx.AsyncClient(
        transport=app, base_url="http://localhost:8000"
    ) as client:
        response = await client.post(
            "users/add",
            content=AddUser_data.model_dump_json(),
            headers={
                "Authorization": f"Bearer {login}",
                "Content-Type": "application/json",
                "accept": "application/json",
            },
        )
    get_user = await services.get_user(txid=AddUser_data.txid, db=db)
    assert response.status_code == 200
    assert AddUser_data.txid == get_user.txid


# there is some issue with this function, not able to test the function
@pytest.mark.asyncio(scope="session")
async def test_edit_user(AddUser_data, EditUser_data, login, db) -> None:
    async with httpx.AsyncClient(
        transport=app, base_url="http://localhost:8000"
    ) as client:
        response = await client.put(
            f"users/?TxnId={AddUser_data.txid}",
            content=EditUser_data.model_dump_json(),
            headers={
                "Authorization": f"Bearer {login}",
                "Content-Type": "application/json",
                "accept": "application/json",
            },
        )
    assert response.status_code == 200
    result = await services.get_user(AddUser_data.txid, db)
    assert result.product == Product.ProductB
    assert result.email_id == "testing_new123@gmail.com"
    assert result.contact_no == "111111111"


@pytest.mark.asyncio(scope="session")
async def test_delete_user(AddUser_data, login, db) -> None:
    async with httpx.AsyncClient(
        transport=app, base_url="http://localhost:8000"
    ) as client:
        response = await client.delete(
            f"users/?TxnId={AddUser_data.txid}",
            headers={"Authorization": f"Bearer {login}"},
        )
    assert response.status_code == 200
    assert await services.get_user(AddUser_data.txid, db) is None
