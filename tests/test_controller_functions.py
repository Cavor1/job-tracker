import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def session_factory():
    engine = create_engine("sqlite:///:memory:")
    return sessionmaker(engine)

