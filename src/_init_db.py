import asyncio

from src.db import database, services
from src.schemas import admins
from src.settings import SUPERUSER_LOGIN, SUPERUSER_PASSWORD

# To add the superuser to newly created database
asyncio.run(
    services.create_admin(
        admins.CreateAdmin(
            username=SUPERUSER_LOGIN,
            scope=admins.Scopes.admin,
            password=SUPERUSER_PASSWORD,
        ),
        database.SessionLocal(),
    )
)

asyncio.run(
    services.create_admin(
        admins.CreateAdmin(
            username="string",
            scope=None,
            password="string",
        ),
        database.SessionLocal(),
    )
)
