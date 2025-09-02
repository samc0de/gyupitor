from fastapi import FastAPI
from celery import Celery
from celery.result import AsyncResult
import os
import sys

# Add the parent directory to the Python path to allow for relative imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from me.crew import Me

app = FastAPI()

# Celery configuration
celery_app = Celery('tasks', broker='redis://redis:6379/0', backend='redis://redis:6379/0')

@celery_app.task
def run_crew_task():
    """Celery task to run the CrewAI crew."""
    try:
        me_crew = Me()
        result = me_crew.crew().kickoff()
        return {"status": "SUCCESS", "result": str(result)}
    except Exception as e:
        return {"status": "FAILURE", "error": str(e)}

@app.post("/start")
async def start_crew():
    """Endpoint to start the CrewAI crew task."""
    task = run_crew_task.delay()
    return {"task_id": task.id}

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    """Endpoint to check the status of a crew task."""
    task_result = AsyncResult(task_id, app=celery_app)
    if task_result.ready():
        return {"status": "SUCCESS", "result": task_result.get()}
    else:
        return {"status": "PENDING"}

@app.get("/")
async def read_root():
    return {"message": "Welcome to the CrewAI BigQuery Analyzer API!"}
