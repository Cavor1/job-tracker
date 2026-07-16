from dataclasses import dataclass, field
from enum import Enum

from src.models import Job, JobEventType, Keyword


class View(Enum):
    MAIN = "main"
    NEW_JOB = "new_job"
    NEW_EVENT = "new_event"


@dataclass
class State:
    jobs: list[Job] = field(default_factory=list)
    current_view: View = View.MAIN
    selected_job_id: int | None = None
    event_types: list[JobEventType] = field(default_factory=list)
    keywords :list[Keyword] = field(default_factory=list)
