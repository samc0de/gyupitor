from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List
import os

from . import crud, models, schemas
from .database import SessionLocal, engine

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- API Routes ---

@app.get("/api/", response_model=str)
def read_root():
    return "Welcome to the BigQuery Cost Optimization API!"

@app.get("/api/query_jobs/", response_model=List[schemas.QueryJob])
def read_query_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query_jobs = crud.get_query_jobs(db, skip=skip, limit=limit)
    return query_jobs

@app.get("/api/query_jobs/{job_id}", response_model=schemas.QueryJobWithDetails)
def read_query_job(job_id: str, db: Session = Depends(get_db)):
    db_query_job = crud.get_query_job(db, job_id)
    if db_query_job is None:
        raise HTTPException(status_code=404, detail="Query Job not found")
    
    db_query_job.raw_query = crud.get_raw_query(db, db_query_job.query_hash)
    db_query_job.execution_timeline = crud.get_execution_timeline(db, db_query_job.job_id)

    return db_query_job

@app.get("/api/query_stats/", response_model=List[schemas.QueryStats])
def read_query_stats(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query_stats = crud.get_query_stats(db, skip=skip, limit=limit)
    return query_stats

@app.get("/api/dashboard_summary/", response_model=schemas.DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    summary = crud.get_dashboard_summary(db)
    return summary

@app.get("/api/daily_costs/", response_model=List[schemas.DailyCost])
def get_daily_costs(days: int = 30, db: Session = Depends(get_db)):
    daily_costs = crud.get_daily_costs(db, days=days)
    return daily_costs

@app.get("/api/project_costs/", response_model=List[schemas.ProjectCost])
def get_project_costs(limit: int = 10, db: Session = Depends(get_db)):
    project_costs = crud.get_project_costs(db, limit=limit)
    return project_costs

@app.get("/api/user_costs/", response_model=List[schemas.UserCost])
def get_user_costs(limit: int = 10, db: Session = Depends(get_db)):
    user_costs = crud.get_user_costs(db, limit=limit)
    return user_costs

# --- Frontend Serving ---

# This must be mounted after all API routes
# It serves the static files built by the frontend
app.mount("/", StaticFiles(directory="static", html=True), name="static")