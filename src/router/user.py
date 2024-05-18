import csv
from datetime import datetime
from typing import Annotated

from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, Depends, File, Response, Security, UploadFile, status
from fastapi.exceptions import HTTPException

from src.db import services
from src.schemas import admins, users
from src.security.license import LicenseGen
from src.security.security import get_current_active_user, get_current_user
from src.settings import CSV_FOLDER
from src.utils import csv_utils

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get("/downloadcsv")
async def get_all_users(
    current_user: Annotated[
        any,
        Security(get_current_user),
    ],
    db: Annotated[any, Depends(services.save_db)],
    txnId: str | None = None,
    product: str | None = None,
    startDate: str | None = None,
    endDate: str | None = None,
    emailId: str | None = None,
    contactNo: str | None = None,
):
    return await services.get_users_all(
        db, txnId, emailId, contactNo, product, startDate, endDate
    )


@router.get("/all")
async def get_users(
    current_user: Annotated[
        any,
        Security(get_current_user),
    ],
    db: Annotated[any, Depends(services.save_db)],
    skip: int = 1,  # This is actually Page Number
    limit: int = 10,  # This is actually Page Size
    txnId: str | None = None,
    product: str | None = None,
    startDate: str | None = None,
    endDate: str | None = None,
    emailId: str | None = None,
    contactNo: str | None = None,
):
    return await services.get_users(
        db, skip, limit, txnId, emailId, contactNo, product, startDate, endDate
    )


@router.get("/")
async def get_user(
    current_user: Annotated[
        any,
        Security(get_current_user),
    ],
    db: Annotated[any, Depends(services.save_db)],
    TxnId: str,
):
    user = await services.get_user(TxnId, db)
    if user is not None:
        return user
    else:
        return {"Error": "User Does not exist or TxID is Invalid!"}


@router.post("/add")
async def add_user(
    db: Annotated[any, Depends(services.save_db)],
    current_user: Annotated[
        any,
        Security(
            get_current_active_user, scopes=[admins.Scopes.edit, admins.Scopes.admin]
        ),
    ],
    adduser: users.AddUser,
    license: Annotated[LicenseGen, Depends()],
):
    data = users.CreateUser(
        txid=adduser.txid,
        amount=adduser.amount,
        payment_method="NA",
        product=adduser.product,
        email_id=adduser.email_id,
        contact_no=adduser.contact_no,
        subscription=adduser.subscription,
        order_date=adduser.order_date,
        License_Key=license.create(adduser.txid + adduser.email_id),
        License_Activated=False,
        Start_Date=adduser.order_date.date(),  # add the actual order date
        End_Date=adduser.order_date.date() + relativedelta(months=adduser.subscription),
    )
    return await services.add_user(data, db)


@router.delete("/")
async def delete_user(
    TxnId: str,
    db: Annotated[any, Depends(services.save_db)],
    current_user: Annotated[
        any,
        Security(
            get_current_active_user, scopes=[admins.Scopes.edit, admins.Scopes.admin]
        ),
    ],
):
    user = await services.get_user(TxnId, db)
    if user is not None:
        await services.delete_user(user, db)
    else:
        return {"Error": "User Does not exist"}


@router.put("/")
async def edit_user(
    TxnId: str,
    edit_user: users.EditUser,
    db: Annotated[any, Depends(services.save_db)],
    current_user: Annotated[
        any,
        Security(
            get_current_active_user, scopes=[admins.Scopes.edit, admins.Scopes.admin]
        ),
    ],
):
    print(edit_user)
    user = await services.get_user(TxnId, db)
    if user is None:
        raise HTTPException(status_code=400, detail="User Does not exist")
        # pass
    else:
        return await services.update_user(user, edit_user, db)


@router.post(
    "/Verifylicence", status_code=status.HTTP_200_OK, tags=["License Key Validation"]
)
async def Verifylicence(
    license_key: users.License,
    db: Annotated[any, Depends(services.save_db)],
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    result = await services.activate_license(license_key, db)
    if result is None:
        raise credentials_exception
    else:
        return result


@router.post("/uploadcsv")
async def upload_CSV(
    current_user: Annotated[
        any,
        Security(
            get_current_active_user, scopes=[admins.Scopes.edit, admins.Scopes.admin]
        ),
    ],
    db: Annotated[any, Depends(services.save_db)],
    Notify_pabbly: bool,
    response: Response,
    license: Annotated[LicenseGen, Depends()],
    file: UploadFile = File(...),
):
    email_ids = []
    file_extension = file.filename.split(".")[-1]  # Getting the uploaded filename
    file_name = file.filename.split(".")[0]  # Getting the uploaded file extension

    if file_extension.lower() != "csv":
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"Message": "Please upload only CSV file"}

    file_location = csv_utils.csv_file_name(file_name)

    try:
        contents = file.file.read()
        with open(file_location, "wb") as f:
            f.write(contents)
    except Exception:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"Message": "There was an error uploading the file"}
    finally:
        file.file.close()

    if csv_utils.header_validator(file_location) == False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "Message": """ Please Upload the CSV file in correct format \n tx_id, user_email, user_phone, amount, order_date, duration, product"""
        }

    data_validation_result = csv_utils.data_validator(file_location)
    if data_validation_result != True:
        response.status_code = status.HTTP_400_BAD_REQUEST
        print(data_validation_result)
        return {"Message": data_validation_result}

    with open(file_location, encoding="utf-8-sig") as f:
        # Now that we have validated the CSV, we are reading the lines one by one
        for RP_reponse in csv.DictReader(f, skipinitialspace=True):
            # print(RP_reponse)

            # Checking user does not exists
            if await services.get_user(RP_reponse["tx_id"], db=db) == None:
                data = users.CreateUser(
                    txid=RP_reponse["tx_id"],
                    amount=RP_reponse["amount"],
                    payment_method="NA",
                    product=RP_reponse["product"],
                    email_id=RP_reponse["user_email"],
                    contact_no=RP_reponse["user_phone"],
                    subscription=RP_reponse["duration"],
                    order_date=datetime.strptime(RP_reponse["order_date"], "%Y-%m-%d"),
                    License_Key=license.create(
                        RP_reponse["tx_id"] + RP_reponse["user_email"]
                    ),
                    License_Activated=False,
                    Start_Date=RP_reponse["order_date"],  # add the actual order date
                    End_Date=datetime.strptime(RP_reponse["order_date"], "%Y-%m-%d")
                    + relativedelta(months=int(RP_reponse["duration"])),
                )
                await services.create_user(data, db=db)
            else:
                email_ids.append(
                    {"tx_id": RP_reponse["tx_id"], "email": RP_reponse["user_email"]}
                )

    if len(email_ids) == 0:
        print({"Message": f"Successfully Uplaoded the CSV file {file_name}"})
        return {"Message": f"Successfully Uplaoded the CSV file {file_name}"}
    else:
        print(
            {
                "Records": email_ids,
                "file_name": file_location,
            }
        )
        return {
            "email_ids": email_ids,
            "file_name": file_location,
        }


@router.post("/uploadcsv_skip_replace")
async def uploadcsv_skip_replace(
    current_user: Annotated[
        any,
        Security(
            get_current_active_user, scopes=[admins.Scopes.edit, admins.Scopes.admin]
        ),
    ],
    db: Annotated[any, Depends(services.save_db)],
    skip_replace_data: users.SkipReplaceUser,
    license: Annotated[LicenseGen, Depends()],
):
    print(skip_replace_data.file_name)
    email_list = skip_replace_data.emails

    for record in email_list:
        if record.replace:
            print("here")
            with open(skip_replace_data.file_name) as f:
                # Now that we have validated the CSV, we are reading the lines one by one
                for row in csv.DictReader(f, skipinitialspace=True):
                    if row["tx_id"] == record.tx_id:
                        await delete_user(row["tx_id"], db=db)
                        data = users.CreateUser(
                            txid=row["tx_id"],
                            amount=row["amount"],
                            payment_method="NA",
                            product=row["product"],
                            email_id=row["user_email"],
                            contact_no=row["user_phone"],
                            subscription=row["duration"],
                            order_date=datetime.strptime(row["order_date"], "%Y-%m-%d"),
                            License_Key=license.create(
                                row["tx_id"] + row["user_email"]
                            ),
                            License_Activated=False,
                            Start_Date=row["order_date"],  # add the actual order date
                            End_Date=datetime.strptime(row["order_date"], "%Y-%m-%d")
                            + relativedelta(months=int(row["duration"])),
                        )
                        await services.create_user(data, db=db)
                        await services.create_user(data, db=db)
