import datetime

from jose import jwt

from src.settings import JWTconfig

# JWT means "JSON Web Tokens".
# It's a standard to codify a JSON object in a long dense string without spaces
# It is not encrypted, so, anyone could recover the information from the contents


def create_access_token(data: dict, expires_delta: datetime.timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.now(datetime.UTC) + expires_delta
    else:
        expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, JWTconfig.SECRET_KEY, algorithm=JWTconfig.ALGORITHM
    )
    return encoded_jwt
