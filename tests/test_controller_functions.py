import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from job_tracker.controller import (
    del_job,
    get_cv_sent_event_type,
    get_event_types,
    get_jobs,
    get_keywords,
    new_job,
    new_job_event,
)
from job_tracker.models import Base, Job, JobEvent, JobEventType, Keyword


@pytest.fixture
def session_factory():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield sessionmaker(engine, expire_on_commit=False)
    engine.dispose()


def test_create_jobs_reuses_keywords_and_initial_event_type(session_factory):
    with session_factory.begin() as session:
        first_id = new_job(session, " First ", " example.com ", [" Python ", "python"])
        second_id = new_job(session, "Second", "example.org", ["python", "sql"])
        assert first_id != second_id

    with session_factory() as session:
        jobs = get_jobs(session)
        assert len(get_keywords(session)) == 2
        assert len(get_event_types(session)) == 1
        assert get_cv_sent_event_type(session).name == "cv_sent"

    # The UI renders these eagerly loaded relationships after the session closes.
    assert jobs[0].title == "First"
    assert jobs[0].link == "example.com"
    assert jobs[0].keywords[0].keyword == "python"
    assert jobs[0].job_events[0].event_type.name == "cv_sent"


def test_caller_can_roll_back_entire_job_creation(session_factory):
    with pytest.raises(RuntimeError, match="Cancel operation"):
        with session_factory.begin() as session:
            new_job(session, "Title", "example.com", ["python"])
            raise RuntimeError("Cancel operation")

    with session_factory() as session:
        for model in (Job, JobEvent, JobEventType, Keyword):
            assert session.scalar(select(func.count()).select_from(model)) == 0


@pytest.mark.parametrize(
    "title,link,keywords",
    [(" ", "example.com", ["python"]), ("Title", " ", ["python"]), ("Title", "example.com", [" "])],
)
def test_invalid_job_raises_without_saving(session_factory, title, link, keywords):
    with pytest.raises(ValueError):
        with session_factory.begin() as session:
            new_job(session, title, link, keywords)

    with session_factory() as session:
        assert get_jobs(session) == []
        assert get_event_types(session) == []
        assert get_keywords(session) == []


def test_event_and_delete_participate_in_callers_transaction(session_factory):
    with session_factory.begin() as session:
        job_id = new_job(session, "Title", "example.com", ["python"])

    with pytest.raises(RuntimeError):
        with session_factory.begin() as session:
            event = JobEvent(event_type=get_cv_sent_event_type(session))
            event.job_id = job_id
            new_job_event(session, event)
            session.flush()
            raise RuntimeError("Cancel event")

    with session_factory() as session:
        assert len(get_jobs(session)[0].job_events) == 1

    with pytest.raises(RuntimeError):
        with session_factory.begin() as session:
            assert del_job(session, job_id)
            session.flush()
            raise RuntimeError("Cancel deletion")

    with session_factory.begin() as session:
        assert len(get_jobs(session)) == 1
        assert del_job(session, job_id)
        assert not del_job(session, job_id + 1)

    with session_factory() as session:
        assert get_jobs(session) == []
        assert session.scalar(select(func.count()).select_from(JobEvent)) == 0
