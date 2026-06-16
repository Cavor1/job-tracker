from dataclasses import dataclass, field
from enum import Enum

from src.models import Job


class View(Enum):
    MAIN = "main"
    NEW_JOB = "new_job"


@dataclass
class State:
    jobs: list[Job] = field(default_factory=list)
    current_view: View = View.MAIN
    selected_job_id: int | None = None
