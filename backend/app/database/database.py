from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import get_settings

settings = get_settings()

# For SQLite, this connect_arg is required to allow usage across
# multiple threads (FastAPI can handle requests concurrently).
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Dependency for FastAPI routes. Yields a database session
    and ensures it's closed after the request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()