import datetime

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from src.db import database, model
from src.schemas import admins, users
from src.security.utils import get_password_hash


def save_db():
    session = database.SessionLocal()
    try:
        yield session
    finally:
        session.close()


async def create_user(user: users.CreateUser, db: Session) -> users.User:
    contact = model.Users(**user.model_dump())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return users.User.model_validate(contact)


async def get_users_all(
    db: Session,
    txnId=None,
    emailId=None,
    contactNo=None,
    product=None,
    startDate=None,
    endDate=None,
):
    filters = []
    if txnId is not None:
        # doing this to make the search case insensitive
        txnId = txnId.lower()
        user = db.query(model.Users).filter(func.lower(model.Users.txid) == txnId).all()
        if user is not None:
            return {"data": user, "total": 1}
        else:
            return {"Error": "User Does not exist or TxID is Invalid!"}

    if contactNo is not None:
        search = "%{}".format(contactNo)

        user = db.query(model.Users).filter(model.Users.contact_no.like(search))
        count = user.count()
        user = user.all()
        if user is not None:
            return {"data": user, "total": count}
        else:
            return {"Error": "User Does not exist or TxID is Invalid!"}

    if emailId is not None:
        emailId = emailId.lower()
        user = db.query(model.Users).filter(func.lower(model.Users.email_id) == emailId)
        count = user.count()
        user = user.all()
        if user is not None:
            return {"data": user, "total": count}
        else:
            return {"Error": "User Does not exist or TxID is Invalid!"}

    if product is not None:
        filters.append(model.Users.product == users.Product[product].value)
    if startDate is not None:
        filters.append(func.date(model.Users.order_date) >= startDate)
    if endDate is not None:
        filters.append(func.date(model.Users.order_date) <= endDate)

    user = db.query(model.Users).filter(and_(*filters))
    filtered_length = user.count()
    user = user.all()

    return {"data": user, "total": filtered_length}


async def get_users(
    db: Session,
    skip=1,  # This is actually Page Number
    limit=10,  # This is actually Page Size
    txnId=None,
    emailId=None,
    contactNo=None,
    product=None,
    startDate=None,
    endDate=None,
):
    # if we don't do -1 then it will skip the first row everytime
    start = (skip - 1) * limit
    filtered_length = 0
    filters = []
    if txnId is not None:
        # doing this to make the search case insensitive
        txnId = txnId.lower()
        user = db.query(model.Users).filter(func.lower(model.Users.txid) == txnId).all()
        if user is not None:
            return {"data": user, "total": 1}
        else:
            return {"Error": "User Does not exist or TxID is Invalid!"}

    if contactNo is not None:
        search = "%{}".format(contactNo)

        user = db.query(model.Users).filter(model.Users.contact_no.like(search))
        count = user.count()
        user = user.all()
        if user is not None:
            return {"data": user, "total": count}
        else:
            return {"Error": "User Does not exist or TxID is Invalid!"}

    if emailId is not None:
        emailId = emailId.lower()
        user = db.query(model.Users).filter(func.lower(model.Users.email_id) == emailId)
        count = user.count()
        user = user.all()
        if user is not None:
            return {"data": user, "total": count}
        else:
            return {"Error": "User Does not exist or TxID is Invalid!"}

    if product is not None:
        filters.append(model.Users.product == users.Product[product].value)
    if startDate is not None:
        filters.append(func.date(model.Users.order_date) >= startDate)
    if endDate is not None:
        filters.append(func.date(model.Users.order_date) <= endDate)

    user = db.query(model.Users).filter(and_(*filters)).order_by(model.Users.id.desc())
    filtered_length = user.count()

    user = user.offset(start).limit(limit).all()
    return {"data": user, "total": filtered_length}


async def add_user(user: users.CreateUser, db: Session) -> users.User:
    temp = await get_user(user.txid, db)
    if temp is None:
        # print("Testing")
        return await create_user(user, db)
    else:
        # print({"Error": "The orderID already Exists!"})
        return {"Error": "The orderID already Exists!"}


async def get_user(txid: str, db: Session) -> users.User:
    user = db.query(model.Users).filter(model.Users.txid == txid).first()
    return user


async def delete_user(user: model.Users, db: Session):
    db.delete(user)
    db.commit()


async def update_user(user: model.Users, edit_user: users.EditUser, db: Session):
    setattr(user, "product", edit_user.product)
    setattr(user, "email_id", edit_user.email_id)
    setattr(user, "contact_no", edit_user.contact_no)
    db.add(user)
    db.commit()
    db.refresh(user)
    return users.User.model_validate(user)


async def activate_license(license: users.License, db: Session) -> list:
    user = (
        db.query(model.Users).filter(model.Users.License_Key == license.license).first()
    )
    # License key not found in the database
    if user is None:
        return None

    else:
        # License Key is expired
        if user.End_Date < datetime.date.today():
            return None

        # Setting the license to activated so that it cannot be used again
        elif user.License_Activated is False:
            user.License_Activated = True
            db.commit()
            return [user.End_Date, user.product]

        # License is already activated
        else:
            return None


async def reset_licence_activated(user: model.Users, db: Session):
    setattr(user, "License_Activated", False)
    db.add(user)
    db.commit()
    db.refresh(user)
    return users.User.model_validate(user)


async def create_admin(admin_data: admins.CreateAdmin, db: Session):
    admin = admins.AdminInDB(
        **admin_data.model_dump(),
        hashed_password=get_password_hash(admin_data.password),
    )
    admin = model.Admins(**admin.model_dump())
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admins.AdminInDB.model_validate(admin)


async def get_admin(admin_username: str, db: Session):
    admin = (
        db.query(model.Admins).filter(model.Admins.username == admin_username).first()
    )
    return admin


async def delete_admin(admin_username: str, db: Session):
    admin = await get_admin(admin_username, db)
    if admin is None:
        return {"Success": f"Admin with username {admin_username} doesn't exist!"}
    else:
        db.delete(admin)
        db.commit()
        return {"Success": f"Admin with username {admin_username} deleted!"}
