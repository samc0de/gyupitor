from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

app = FastAPI()

class QueryRequest(BaseModel):
    query_id: str

@app.get("/")
async def read_root():
    return {"message": "Welcome to the BigQuery Application API!"}

@app.post("/query")
async def handle_query(request: QueryRequest):
    """
    Handles a query request, simulating interaction with BigQuery Materialized View.
    In a real scenario, this would query BigQuery, potentially using a caching layer.
    """
    query_id = request.query_id
    
    # Simulate a cache hit/miss and BigQuery lookup
    if query_id == "fast_query":
        response_data = {"query_id": query_id, "status": "success", "data": {"result": "Data from Materialized View (fast)"}}
    elif query_id == "slow_query":
        # This would typically be a cache miss leading to a BigQuery MV lookup
        response_data = {"query_id": query_id, "status": "success", "data": {"result": "Data from Materialized View (slow, simulated)"}}
    else:
        raise HTTPException(status_code=404, detail="Query ID not found")
        
    return response_data

# This is for local development/testing with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
