from sqlalchemy import Integer, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from pathlib import Path

BASE_PATH = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_PATH / "database" / "job_tracker.db"


class Base(DeclarativeBase):
    pass

class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    title: Mapped[str]

job1 = Job(title = "Python dev")
job2 = Job(title = None)

engine = create_engine(f"sqlite:///{DATABASE_PATH}")

Base.metadata.create_all(engine)

with Session(engine) as session:
    session.add(job1)
    session.commit()

with Session(engine) as session:
    print([f'{j.id},{j.title}' for j in session.query(Job).all()])