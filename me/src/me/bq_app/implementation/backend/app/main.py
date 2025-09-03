from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import os

app = FastAPI()

# Enable CORS for all origins, allowing the frontend to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in a production environment
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"]
)

@app.get("/api/recommendations")
async def get_recommendations():
    # Construct the path to recommendations.json
    # This assumes recommendations.json is in the parent directory of main.py's directory (app)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    recommendations_file_path = os.path.join(current_dir, "..", "recommendations.json")
    
    try:
        with open(recommendations_file_path, "r") as f:
            recommendations = json.load(f)
        return JSONResponse(content=recommendations)
    except FileNotFoundError:
        return JSONResponse(content={"error": "recommendations.json not found"}, status_code=404)
    except json.JSONDecodeError:
        return JSONResponse(content={"error": "Error decoding recommendations.json"}, status_code=500)
