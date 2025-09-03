import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development purposes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RECOMMENDATIONS_FILE = "/app/analysis/recommendations.json" # Path inside the Docker container

@app.get("/api/recommendations")
async def get_recommendations():
    if not os.path.exists(RECOMMENDATIONS_FILE):
        raise HTTPException(status_code=404, detail=f"Recommendations file not found at {RECOMMENDATIONS_FILE}")
    try:
        with open(RECOMMENDATIONS_FILE, "r") as f:
            recommendations = json.load(f)
        return recommendations
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error decoding recommendations JSON")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.get("/")
async def root():
    return {"message": "BigQuery Recommendations Backend is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
