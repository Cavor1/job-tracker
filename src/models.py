from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    mapped_column,
    relationship,
)


class Base(MappedAsDataclass, DeclarativeBase):
    pass


job_keywords = Table(
    "job_keywords",
    Base.metadata,
    Column("job_id", ForeignKey("jobs.id"), primary_key=True),
    Column("keyword_id", ForeignKey("keywords.id"), primary_key=True),
)


class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    title: Mapped[str]
    link: Mapped[str]
    cv: Mapped[str | None] = mapped_column(default=None)
    company: Mapped[str | None] = mapped_column(default=None)
    description: Mapped[str | None] = mapped_column(default=None)
    rejected: Mapped[bool | None] = mapped_column(default=None)
    date_created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default_factory=lambda: datetime.now(timezone.utc),
        init=False,
    )
    keywords: Mapped[list[Keyword]] = relationship(
        secondary=job_keywords, back_populates="jobs", default_factory=list
    )


class Keyword(Base):
    __tablename__ = "keywords"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    keyword: Mapped[str] = mapped_column(String, unique=True)
    jobs: Mapped[list[Job]] = relationship(
        secondary=job_keywords, back_populates="keywords", default_factory=list
    )
