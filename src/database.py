from sqlalchemy import create_engine
from pathlib import Path

from sqlalchemy.orm import sessionmaker
from src.models import Base

BASE_PATH = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_PATH / "database" / "job_tracker.db"

engine = create_engine(f"sqlite:///{DATABASE_PATH}")
SessionLocal = sessionmaker(engine)

def create_tables():
    Base.metadata.create_all(engine)
#

# job1 = Job(title = "Python dev")
# with Session(engine) as session:
#     session.add(job1)
#     session.commit()
