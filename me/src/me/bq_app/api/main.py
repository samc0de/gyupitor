import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from apscheduler.schedulers.background import BackgroundScheduler
import meilisearch

# --- Configuration ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MEILISEARCH_HOST = os.getenv("MEILISEARCH_HOST", "http://127.0.0.1:7700")
MEILISEARCH_API_KEY = os.getenv("MEILISEARCH_API_KEY", "aSampleMasterKey")

# --- Meilisearch Client Setup ---
client = meilisearch.Client(MEILISEARCH_HOST, MEILISEARCH_API_KEY)

# --- Pydantic Data Models ---
class Job(BaseModel):
    job_id: str = Field(..., description="Unique ID for the BigQuery job")
    project_id: str
    query: str
    normalized_query_hash: str
    total_bytes_billed: int
    total_slot_ms: int
    creation_time: str

class Recommendation(BaseModel):
    recommendation_id: str = Field(..., description="Unique ID for the recommendation")
    recommendation_type: str = Field(..., description="e.g., PARTITION_TABLE, CREATE_MATERIALIZED_VIEW, REWRITE_QUERY")
    project_id: str
    status: str = Field(default="new", description="e.g., new, implemented, dismissed")
    details: dict
    estimated_savings_usd: float

# --- FastAPI App Initialization ---
app = FastAPI(
    title="BigQuery Cost Optimizer",
    description="An application to analyze BigQuery usage and provide cost-saving recommendations.",
    version="0.1.0"
)

# --- Periodic Job Logic ---
def analyze_bigquery_data():
    """
    This is the core logic that runs periodically.
    1. In a real scenario, this would connect to BigQuery's INFORMATION_SCHEMA.
    2. For this demo, we'll simulate fetching data and creating a recommendation.
    3. It will process the data to identify optimization opportunities.
    4. It will then create and store recommendations in Meilisearch.
    """
    logger.info("Starting periodic analysis of BigQuery data...")

    # --- 1. Simulate fetching data from BigQuery ---
    # This data is based on the provided analysis report.
    simulated_jobs = [
        {
            'job_id': 'job_12345',
            'project_id': 'onspend',
            'query': "SELECT * FROM `onspend.GCPspendexport.gcp_billing_export_v1_007599_AE5FA0_17030D` WHERE invoice.month = '202307'",
            'normalized_query_hash': '81222...',
            'total_bytes_billed': 134500000000, # 134.5 GB
            'total_slot_ms': 3600000,
            'creation_time': '2023-10-26T10:00:00Z'
        }
    ]

    # --- 2. Add fetched jobs to Meilisearch ---
    jobs_index = client.index('jobs')
    jobs_index.add_documents([job for job in simulated_jobs], primary_key='job_id')
    logger.info(f"Added {len(simulated_jobs)} jobs to the 'jobs' index.")

    # --- 3. Simulate analysis and recommendation generation ---
    # Here, we'd have logic to detect patterns like `SELECT *` or lack of a WHERE clause on a partitioned field.
    # For this example, we'll create a recommendation for the simulated job.
    simulated_recommendation = {
        'recommendation_id': 'rec_partition_onspend_billing',
        'recommendation_type': 'PARTITION_TABLE',
        'project_id': 'onspend',
        'status': 'new',
        'details': {
            'table_name': 'onspend.GCPspendexport.gcp_billing_export_v1_007599_AE5FA0_17030D',
            'recommendation': 'Partition the table by `usage_start_time` on a DAY granularity and cluster by `project.id`.',
            'reasoning': 'Query `81222...` is a full table scan. Partitioning will prune the data scanned significantly.'
        },
        'estimated_savings_usd': 715000.00
    }

    # --- 4. Add recommendation to Meilisearch ---
    recommendations_index = client.index('recommendations')
    recommendations_index.add_documents([simulated_recommendation], primary_key='recommendation_id')
    logger.info("Generated and stored a new recommendation.")

# --- Scheduler Setup ---
scheduler = BackgroundScheduler()
scheduler.add_job(analyze_bigquery_data, 'interval', minutes=60) # Run every hour
scheduler.start()

# --- API Endpoints ---
@app.on_event("startup")
async def startup_event():
    # A simple check to see if Meilisearch is available
    try:
        client.health()
        logger.info("Successfully connected to Meilisearch.")
        # Optional: Configure indexes on startup
        jobs_index = client.index('jobs')
        jobs_index.update_filterable_attributes(['project_id', 'normalized_query_hash'])
        recs_index = client.index('recommendations')
        recs_index.update_filterable_attributes(['project_id', 'status', 'recommendation_type'])
    except Exception as e:
        logger.error(f"Could not connect to Meilisearch: {e}")

@app.get("/", summary="Root endpoint for health check")
def read_root():
    return {"status": "ok", "message": "BigQuery Cost Optimizer API is running."}

@app.get("/recommendations/", response_model=List[Recommendation], summary="Search for recommendations")
async def search_recommendations(project_id: Optional[str] = None, status: Optional[str] = None):
    index = client.index('recommendations')
    search_params = {}
    filter_conditions = []
    if project_id:
        filter_conditions.append(f'project_id = {project_id}')
    if status:
        filter_conditions.append(f'status = {status}')
    
    if filter_conditions:
        search_params['filter'] = ' AND '.join(filter_conditions)

    results = index.search('', search_params)
    return results.get('hits', [])

@app.get("/jobs/", response_model=List[Job], summary="Search for processed jobs")
async def search_jobs(project_id: Optional[str] = None, query_hash: Optional[str] = None):
    index = client.index('jobs')
    search_params = {}
    filter_conditions = []
    if project_id:
        filter_conditions.append(f'project_id = {project_id}')
    if query_hash:
        filter_conditions.append(f'normalized_query_hash = {query_hash}')

    if filter_conditions:
        search_params['filter'] = ' AND '.join(filter_conditions)

    results = index.search('', search_params)
    return results.get('hits', [])

@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()
