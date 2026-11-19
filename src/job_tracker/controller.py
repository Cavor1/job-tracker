"""Application operations using caller-owned sessions and transactions."""

from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from job_tracker.logger import log
from job_tracker.models import Job, JobEvent, JobEventType, Keyword


def get_jobs(session: Session) -> list[Job]:
    return list(
        session.scalars(
            select(Job).options(
                selectinload(Job.job_events).selectinload(JobEvent.event_type),
                selectinload(Job.keywords),
            )
        ).all()
    )


def get_event_types(session: Session) -> list[JobEventType]:
    return list(session.scalars(select(JobEventType)).all())


def new_job(
    session: Session,
    title: str,
    link: str,
    keywords: Iterable[str],
    company: str | None = None,
    description: str | None = None,
) -> int:
    error = ""

    if not title.strip():
        error += "Title cant be empty or only whitespace.\n"

    if not link.strip():
        error += "link cant be empty or only whitespace.\n"

    keywords_set: set[str] = {kw.strip().lower() for kw in keywords if kw.strip()}

    if not keywords_set:
        error += "keywords cant be empty or only whitespace.\n"

    if error:
        raise ValueError(error)

    db_keywords = get_keywords(session)
    db_keywords_by_name = {kw.keyword: kw for kw in db_keywords}
    job_keywords: list[Keyword] = []

    for keyword_text in keywords_set:
        if keyword_text in db_keywords_by_name:
            keyword = db_keywords_by_name[keyword_text]

        else:
            keyword = Keyword(keyword=keyword_text)
            db_keywords_by_name[keyword_text] = keyword

        job_keywords.append(keyword)
    
    company = (company or "").strip() or None #whitespaces turn to None

    event_type = get_cv_sent_event_type(session)
    job = Job(title=title.strip(), link=link.strip(), company=company, description=description, keywords=job_keywords)
    
    job.job_events.append(JobEvent(event_type=event_type))
    session.add(job)
    session.flush()
    return job.id


def new_job_event(session: Session, job_event: JobEvent) -> None:
    session.add(job_event)


def del_job(session: Session, job_id: int) -> bool:
    job = session.get(Job, job_id)
    if job is None:
        return False
    session.delete(job)
    return True


def get_cv_sent_event_type(session: Session) -> JobEventType:
    log("getting event type")
    cv_sent_type = session.scalar(
        select(JobEventType).where(JobEventType.name == "cv_sent")
    )
    if cv_sent_type is None:
        log("creating new one")
        cv_sent_type = JobEventType("cv_sent")
        session.add(cv_sent_type)
    return cv_sent_type


def get_keywords(session: Session) -> list[Keyword]:
    return list(session.scalars(select(Keyword)).all())
