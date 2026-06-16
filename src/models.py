from sqlalchemy import Column, ForeignKey, Integer, String, Table
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
    company: Mapped[str]
    description: Mapped[str | None]
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
