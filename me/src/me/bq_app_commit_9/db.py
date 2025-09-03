import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Get the absolute path to the database file.
# The database file is expected to be in the parent directory of this script's location.
SQLALCHEMY_DATABASE_URL = "sqlite:////app/db_data/bq_analyzer.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
