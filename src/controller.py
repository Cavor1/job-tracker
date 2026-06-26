from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload, sessionmaker

from src.database import SessionLocal
from src.logger import log
from src.models import Job, JobEvent, JobEventType, Keyword


def get_jobs(
    session_factory: sessionmaker[Session] = SessionLocal,
) -> list[Job]:
    with session_factory() as session:
        return list(
            session.execute(
                select(Job).options(
                    selectinload(Job.job_events).selectinload(JobEvent.event_type)
                )
            )
            .scalars()
            .all()
        )


def new_job(job: Job, session_factory: sessionmaker[Session] = SessionLocal):
    with session_factory() as session:
        session.add(job)
        session.commit()

def get_cv_sent_event_type(session_factory : sessionmaker[Session] = SessionLocal) -> JobEventType:
    log("getting event type")
    cv_sent_type = None
    with session_factory() as session:
        cv_sent_type = session.scalar(select(JobEventType).where(JobEventType.name == "cv_sent"))
        log("got event type")
    
    if cv_sent_type is None:
        log("creating new one")
        cv_sent_type = JobEventType("cv_sent")
        with session_factory() as session:
            session.add(cv_sent_type)
            session.commit()

    return cv_sent_type


def get_keywords(
    session_factory: sessionmaker[Session] = SessionLocal,
) -> list[Keyword]:
    keywords = []
    with session_factory() as session:
        keywords = list(session.execute(select(Keyword)).scalars().all())
    return keywords
