
from datetime import UTC, datetime
from sqlalchemy import select

from job_tracker.database import SessionLocal
from job_tracker.models import Job, JobEvent, JobEventType


def get_next_or_last_event(job : Job) -> JobEvent:

    now = datetime.now(UTC)
    past_events = [j for j in job.job_events if j.date.replace(tzinfo=UTC) < now]
    future_events = [j for j in job.job_events if j.date.replace(tzinfo=UTC) >= now]

    # next future event or last event if no future events.
    event : JobEvent | None= (
        max(past_events, key=lambda e: e.date, default=None)
        if not future_events
        else min(future_events, key=lambda e: e.date)
    )
    if event is None:
        raise ValueError("Job has no events")

    return event

COMMON_EVENT_TYPES = [
    "cv_sent",
    "cv_response",
    "interview",
    "exam",
    "techical_task",
    "rejected",
    "accepted",
]


def seed_job_event_types() -> None:
    with SessionLocal() as session:
        existing_names = set(
            session.scalars(
                select(JobEventType.name)
            ).all()
        )

        for name in COMMON_EVENT_TYPES:
            if name not in existing_names:
                session.add(JobEventType(name=name))

        session.commit()


if __name__ == "__main__":
    seed_job_event_types()