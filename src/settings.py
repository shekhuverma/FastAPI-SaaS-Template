import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

DEBUG = os.getenv("DEBUG")

SUPERUSER_LOGIN = os.getenv("SUPERUSER_LOGIN")
SUPERUSER_PASSWORD = os.getenv("SUPERUSER_PASSWORD")

CSV_FOLDER = "CSV_Uploads"


class JWTconfig(BaseSettings):
    # to get a string like this run:
    # openssl rand -hex 32
    SECRET_KEY: str = "9ebde6d2b2e67230fa346e926bbbdf64eee1c0baaf7b3db6d14d8890aff26066"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    ALGORITHM: str = "HS256"

    model_config = SettingsConfigDict(case_sensitive=True)


class LicenseGenSettings(BaseSettings):
    # must be 16/24/32 bytes long
    SECRET_KEY: str = "abcdefghijklmnop"

    # must be 16 bytes long
    INITIALISATION_VECTOR: str = "qrstuvwxyzabcdef"


def get_db_url():
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "")
    server = os.getenv("POSTGRES_SERVER", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "app")

    return f"postgresql://{user}:{password}@{server}:{port}/{db}"


JWTconfig = JWTconfig()
LicenseGenSettings = LicenseGenSettings()
