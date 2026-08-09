
from datetime import UTC, datetime

from src.models import Job, JobEvent


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