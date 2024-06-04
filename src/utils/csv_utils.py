import csv
import os
from datetime import datetime

from dateutil.relativedelta import relativedelta

from src.schemas import users
from src.settings import CSV_FOLDER

CORRECT_HEADER = [
    "tx_id",
    "user_email",
    "user_phone",
    "amount",
    "order_date",
    "duration",
    "product",
]


def csv_file_name(uploaded_filename: str, extension=".csv"):
    return os.path.join(
        CSV_FOLDER,
        uploaded_filename + "_" + datetime.now().strftime("%Y%m%d%H%M%S") + extension,
    )


def header_validator(csv_file_path) -> bool:
    with open(csv_file_path, encoding="utf-8-sig") as f:
        headers = csv.DictReader(f).fieldnames
        print(headers)
        if headers != CORRECT_HEADER:
            return False
    return True


def data_validator(csv_file_path):
    with open(csv_file_path, encoding="utf-8-sig") as f:
        for RP_reponse in csv.DictReader(f, skipinitialspace=True):
            try:
                data = users.CreateUser(  # noqa: F841
                    txid=RP_reponse["tx_id"],
                    amount=RP_reponse["amount"],
                    payment_method="NA",
                    product=RP_reponse["product"],
                    email_id=RP_reponse["user_email"],
                    contact_no=RP_reponse["user_phone"],
                    subscription=RP_reponse["duration"],
                    order_date=datetime.strptime(RP_reponse["order_date"], "%Y-%m-%d"),
                    License_Key="temp_license",
                    License_Activated=False,
                    Start_Date=RP_reponse["order_date"],  # add the actual order date
                    End_Date=datetime.strptime(RP_reponse["order_date"], "%Y-%m-%d")
                    + relativedelta(months=int(RP_reponse["duration"])),
                )
            except ValueError as e:
                return f"{e} in row {RP_reponse}"

    return True
