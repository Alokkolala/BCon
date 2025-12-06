"""Database initialization and session management."""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


auth_engine = None
SessionLocal = None


class Base(DeclarativeBase):
    pass


def init_engine(database_url: str):
    global auth_engine, SessionLocal
    auth_engine = create_engine(database_url, future=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=auth_engine, expire_on_commit=False)
    return auth_engine


def get_session():
    if SessionLocal is None:
        raise RuntimeError("Database engine has not been initialized")
    return SessionLocal()
