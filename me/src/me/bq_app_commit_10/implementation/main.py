from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import os

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:80",
    "http://localhost:3000", # For potential React dev server
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/recommendations")
def get_recommendations():
    # Construct the path to recommendations.json relative to the current script
    # The analysis directory is a sibling of the implementation directory
    script_dir = os.path.dirname(__file__)
    json_path = os.path.join(script_dir, "..", "analysis", "recommendations.json")
    
    # Ensure the path is absolute and normalized
    json_path = os.path.abspath(json_path)

    if not os.path.exists(json_path):
        # Log an error or return a specific error response if the file is not found
        print(f"Error: recommendations.json not found at {json_path}")
        return {"error": "Recommendations file not found"}

    with open(json_path) as f:
        data = json.load(f)
    return data
