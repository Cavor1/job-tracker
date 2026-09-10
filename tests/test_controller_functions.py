import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from job_tracker.models import Job


@pytest.fixture
def session_factory():
    engine = create_engine("sqlite:///:memory:")
    return sessionmaker(engine)

