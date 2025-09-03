from sqlalchemy import Column, String, BigInteger, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class QueryJob(Base):
    __tablename__ = "query_jobs"

    job_id = Column(String, primary_key=True, index=True)
    query_hash = Column(String, ForeignKey("raw_queries.query_hash"), index=True)
    project_id = Column(String)
    user_email = Column(String)
    total_bytes_billed = Column(BigInteger)
    total_slot_ms = Column(BigInteger)
    creation_time = Column(TIMESTAMP)
    start_time = Column(TIMESTAMP)
    end_time = Column(TIMESTAMP)
    timeline_details_file = Column(String)

    raw_query = relationship("RawQuery", back_populates="query_jobs", primaryjoin="QueryJob.query_hash == RawQuery.query_hash")
    execution_timeline = relationship("ExecutionTimeline", back_populates="query_job", uselist=False)

class RawQuery(Base):
    __tablename__ = "raw_queries"

    query_hash = Column(String, primary_key=True, index=True)
    query_text = Column(Text, nullable=False)

    query_jobs = relationship("QueryJob", back_populates="raw_query", primaryjoin="RawQuery.query_hash == QueryJob.query_hash")

class ExecutionTimeline(Base):
    __tablename__ = "execution_timelines"

    job_id = Column(String, ForeignKey("query_jobs.job_id"), primary_key=True, index=True)
    timeline_json = Column(Text, nullable=False)

    query_job = relationship("QueryJob", back_populates="execution_timeline")