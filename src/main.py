from typing import Annotated

from fastapi import Depends, FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse  # for example

from src.db import services
from src.docs.docs import tags_metadata
from src.router import admin, user
from src.security.license import LicenseGen

app = FastAPI(openapi_tags=tags_metadata)


@app.exception_handler(RequestValidationError)
async def value_error_exception_handler(request: Request, exc: RequestValidationError):
    error = exc.errors()[0]
    print(error)
    return JSONResponse(
        status_code=400,
        content={"Message": f"Error in {error['loc'][1]}, {error['msg']}"},
    )


origins = ["http://localhost", "http://localhost:8000", "http://localhost:3000", "*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin.router)
app.include_router(user.router)


# Just for testing the public IP
@app.get("/", tags=["Testing"])
def read_root():
    return {"Hello": "World"}


# To create a new user using webhook trigger
@app.post("/webhook", status_code=status.HTTP_202_ACCEPTED, tags=["Webhook"])
async def webhook(
    request: Request,
    db: Annotated[any, Depends(services.save_db)],
    license: Annotated[LicenseGen, Depends()],
):
    result = await request.json()
    print(result)
    return result

    # Example of how to create a new user whenever the webhook is triggered
    # product_name = "For testing"

    # orderDate = datetime.strptime(
    #     result["date_completed"].split()[0], "%Y-%m-%d"
    # ).date()
    # data = users.CreateUser(
    #     txid=result["transaction_id"],
    #     amount=result["total"],
    #     payment_method="NA",
    #     product=product_name,
    #     email_id=result["billing_email"],
    #     contact_no=result["billing_phone"],
    #     subscription=12,
    #     order_date=result["date_completed"],
    #     License_Key=license.create(result["transaction_id"] + result["billing_email"]),
    #     License_Activated=False,
    #     Start_Date=orderDate,  # add the actual order date
    #     End_Date=orderDate + relativedelta(months=12),
    # )
    # # to give the data to some other automation service, fox ex pabbly
    # pabbly_data = data.model_dump()
    # pabbly_trigger(pabbly_data)
    # return await services.create_user(data, db=db)
