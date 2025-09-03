from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from . import models, schemas
from datetime import datetime, timedelta

def get_query_job(db: Session, job_id: str):
    return db.query(models.QueryJob).filter(models.QueryJob.job_id == job_id).first()

def get_query_jobs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.QueryJob).offset(skip).limit(limit).all()

def create_query_job(db: Session, job: schemas.QueryJobCreate):
    db_job = models.QueryJob(**job.model_dump())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

def get_raw_query(db: Session, query_hash: str):
    return db.query(models.RawQuery).filter(models.RawQuery.query_hash == query_hash).first()

def create_raw_query(db: Session, raw_query: schemas.RawQueryCreate):
    db_raw_query = models.RawQuery(**raw_query.model_dump())
    db.add(db_raw_query)
    db.commit()
    db.refresh(db_raw_query)
    return db_raw_query

def get_execution_timeline(db: Session, job_id: str):
    return db.query(models.ExecutionTimeline).filter(models.ExecutionTimeline.job_id == job_id).first()

def create_execution_timeline(db: Session, timeline: schemas.ExecutionTimelineCreate):
    db_timeline = models.ExecutionTimeline(**timeline.model_dump())
    db.add(db_timeline)
    db.commit()
    db.refresh(db_timeline)
    return db_timeline

def get_query_stats(db: Session, skip: int = 0, limit: int = 100):
    # This query groups by query_hash and calculates aggregates
    # It also joins with raw_queries to get a snippet of the query text
    return (
        db.query(
            models.QueryJob.query_hash,
            func.sum(models.QueryJob.total_bytes_billed).label("total_bytes_billed"),
            func.sum(models.QueryJob.total_slot_ms).label("total_slot_ms"),
            func.count(models.QueryJob.job_id).label("job_count"),
            func.avg(models.QueryJob.total_bytes_billed).label("avg_bytes_billed"),
            func.avg(models.QueryJob.total_slot_ms).label("avg_slot_ms"),
            models.RawQuery.query_text.label("query_text_snippet"),
        )
        .join(models.RawQuery, models.QueryJob.query_hash == models.RawQuery.query_hash)
        .group_by(models.QueryJob.query_hash, models.RawQuery.query_text)
        .order_by(desc(func.sum(models.QueryJob.total_bytes_billed)))
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_daily_costs(db: Session, days: int = 30):
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    return (
        db.query(
            func.strftime("%Y-%m-%d", models.QueryJob.creation_time).label("date"),
            func.sum(models.QueryJob.total_bytes_billed).label("total_bytes_billed"),
        )
        .filter(models.QueryJob.creation_time >= start_date)
        .group_by(func.strftime("%Y-%m-%d", models.QueryJob.creation_time))
        .order_by(func.strftime("%Y-%m-%d", models.QueryJob.creation_time))
        .all()
    )

def get_project_costs(db: Session, limit: int = 10):
    return (
        db.query(
            models.QueryJob.project_id,
            func.sum(models.QueryJob.total_bytes_billed).label("total_bytes_billed"),
        )
        .group_by(models.QueryJob.project_id)
        .order_by(desc(func.sum(models.QueryJob.total_bytes_billed)))
        .limit(limit)
        .all()
    )

def get_user_costs(db: Session, limit: int = 10):
    return (
        db.query(
            models.QueryJob.user_email,
            func.sum(models.QueryJob.total_bytes_billed).label("total_bytes_billed"),
        )
        .group_by(models.QueryJob.user_email)
        .order_by(desc(func.sum(models.QueryJob.total_bytes_billed)))
        .limit(limit)
        .all()
    )

def get_dashboard_summary(db: Session):
    total_bytes_billed = db.query(func.sum(models.QueryJob.total_bytes_billed)).scalar()
    total_queries_analyzed = db.query(func.count(models.QueryJob.job_id)).scalar()
    last_analyzed_date = db.query(func.max(models.QueryJob.creation_time)).scalar()

    # Top spender
    top_spender = db.query(
        models.QueryJob.user_email,
        func.sum(models.QueryJob.total_bytes_billed).label("total_bytes_billed")
    ).group_by(models.QueryJob.user_email).order_by(desc("total_bytes_billed")).first()

    total_cost_tb = (total_bytes_billed / (1024**4)) if total_bytes_billed else 0 # Convert bytes to TB
    top_spender_cost_tb = (top_spender.total_bytes_billed / (1024**4)) if top_spender else 0

    return schemas.DashboardSummary(
        total_cost_tb=total_cost_tb,
        total_queries_analyzed=total_queries_analyzed or 0,
        top_spender_email=top_spender.user_email if top_spender else None,
        top_spender_cost_tb=top_spender_cost_tb,
        last_analyzed_date=last_analyzed_date
    )