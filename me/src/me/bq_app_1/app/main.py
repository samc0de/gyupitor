from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "BigQuery Cost Optimization Backend is running!"}

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "BigQuery Cost Optimization API"}
