from sqlalchemy import select

from src.database import SessionLocal
from src.models import JobEventType


COMMON_EVENT_TYPES = [
    "app_sent",
    "app_response",
    "interview",
    "exam",
    "techical_task"
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