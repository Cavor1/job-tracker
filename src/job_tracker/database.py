from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from job_tracker.models import Base

import os

from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH")

engine = create_engine(f"sqlite:///{DB_PATH}")
SessionLocal = sessionmaker(engine,expire_on_commit=False)


def create_tables():
    Base.metadata.create_all(engine)
