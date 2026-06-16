from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from src.database import SessionLocal
from src.models import Job, Keyword


def get_jobs(session_factory: sessionmaker[Session] = SessionLocal) -> list[Job]:
    jobs = []
    with session_factory() as session:
        jobs = list(session.execute(select(Job)).scalars().all())
    return jobs


def new_job(job: Job, session_factory: sessionmaker[Session] = SessionLocal):
    with session_factory() as session:
        session.add(Job)
        session.commit()


def get_keywords(
    session_factory: sessionmaker[Session] = SessionLocal,
) -> list[Keyword]:
    keywords = []
    with session_factory() as session:
        keywords = list(session.execute(select(Keyword)).scalars().all())
    return keywords
