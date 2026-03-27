import os
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Grabs the DATABASE_URL environment variable provided by the Docker container
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://lms_user:lms_password@db:5432/lms_db")

# Create the SQLAlchemy engine, implementing retries to wait for the Postgres container to boot
def get_engine():
    retries = 5
    while retries > 0:
        try:
            engine = create_engine(DATABASE_URL)
            engine.connect()
            return engine
        except Exception as e:
            retries -= 1
            time.sleep(2)
    raise Exception("Database connection failed")

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency function to provide a database session to API endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()