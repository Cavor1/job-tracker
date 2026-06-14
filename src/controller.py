from sqlalchemy import select

from src.database import SessionLocal
from src.models import Job


def get_jobs() -> list[Job]:
    jobs = []
    with SessionLocal() as session:
        jobs = list(session.execute(select(Job)).scalars().all())
    return jobs