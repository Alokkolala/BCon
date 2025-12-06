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


def load_settings() -> Settings:
    """Load configuration from environment variables."""
    client_id = os.getenv("PLAID_CLIENT_ID", "")
    secret = os.getenv("PLAID_SECRET", "")
    environment = os.getenv("PLAID_ENV", "sandbox")
    redirect_uri = os.getenv("PLAID_REDIRECT_URI")
    database_url = os.getenv("DATABASE_URL", "sqlite:///bankconnect.db")
    encryption_key = os.getenv("ENCRYPTION_KEY", "")

    if not client_id or not secret:
        raise RuntimeError("PLAID_CLIENT_ID and PLAID_SECRET must be set for Plaid integration.")
    if not encryption_key:
        raise RuntimeError("ENCRYPTION_KEY must be set for encrypting sensitive data.")

    plaid_settings = PlaidSettings(
        client_id=client_id,
        secret=secret,
        environment=environment,
        redirect_uri=redirect_uri,
    )
    return Settings(database_url=database_url, plaid=plaid_settings, encryption_key=encryption_key)
