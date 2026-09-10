from dataclasses import dataclass, field
from enum import Enum

from job_tracker.controller import (
    get_cv_sent_event_type,
    get_event_types,
    get_jobs,
    get_keywords,
)
from job_tracker.logger import log
from job_tracker.models import Job, JobEventType, Keyword
from job_tracker.utils import get_next_or_last_event


class View(Enum):
    MAIN = "main"
    NEW_JOB = "new_job"
    NEW_EVENT = "new_event"


@dataclass
class State:
    cv_sent_type : JobEventType
    jobs: list[Job] = field(default_factory=list)
    jobs_visible : list[Job] = field(default_factory=list)
    current_view: View = View.MAIN
    selected_job_id: int | None = None
    event_types: list[JobEventType] = field(default_factory=list)
    keywords :list[Keyword] = field(default_factory=list)



def load_state(state : State | None = None): 
    state = state or State(get_cv_sent_event_type())

    state.jobs = get_jobs()
    state.jobs_visible  = sorted(state.jobs, reverse=True,key=lambda j: get_next_or_last_event(j).date)
    state.event_types = get_event_types()
    log(str([et.name for et in state.event_types]))
    state.keywords = get_keywords()

    return state
