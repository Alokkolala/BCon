"""Backend configuration for BankConnect."""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class PlaidSettings:
    client_id: str
    secret: str
    environment: str = "sandbox"
    redirect_uri: Optional[str] = None


@dataclass
class Settings:
    database_url: str
    plaid: PlaidSettings
    encryption_key: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_exp_minutes: int = 60
    password_reset_exp_minutes: int = 30
    oauth_google_client_id: Optional[str] = None
    oauth_google_client_secret: Optional[str] = None


def load_settings() -> Settings:
    """Load configuration from environment variables."""
    client_id = os.getenv("PLAID_CLIENT_ID", "")
    secret = os.getenv("PLAID_SECRET", "")
    environment = os.getenv("PLAID_ENV", "sandbox")
    redirect_uri = os.getenv("PLAID_REDIRECT_URI")
    database_url = os.getenv("DATABASE_URL", "sqlite:///bankconnect.db")
    encryption_key = os.getenv("ENCRYPTION_KEY", "")
    jwt_secret = os.getenv("JWT_SECRET", "")
    jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_exp_minutes = int(os.getenv("JWT_EXP_MINUTES", "60"))
    password_reset_exp_minutes = int(os.getenv("PASSWORD_RESET_EXP_MINUTES", "30"))
    oauth_google_client_id = os.getenv("OAUTH_GOOGLE_CLIENT_ID")
    oauth_google_client_secret = os.getenv("OAUTH_GOOGLE_CLIENT_SECRET")

    if not client_id or not secret:
        raise RuntimeError("PLAID_CLIENT_ID and PLAID_SECRET must be set for Plaid integration.")
    if not encryption_key:
        raise RuntimeError("ENCRYPTION_KEY must be set for encrypting sensitive data.")
    if not jwt_secret:
        raise RuntimeError("JWT_SECRET must be set for issuing authentication tokens.")

    plaid_settings = PlaidSettings(
        client_id=client_id,
        secret=secret,
        environment=environment,
        redirect_uri=redirect_uri,
    )
    return Settings(
        database_url=database_url,
        plaid=plaid_settings,
        encryption_key=encryption_key,
        jwt_secret=jwt_secret,
        jwt_algorithm=jwt_algorithm,
        jwt_exp_minutes=jwt_exp_minutes,
        password_reset_exp_minutes=password_reset_exp_minutes,
        oauth_google_client_id=oauth_google_client_id,
        oauth_google_client_secret=oauth_google_client_secret,
    )
