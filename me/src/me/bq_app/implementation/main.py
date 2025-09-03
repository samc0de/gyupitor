from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import os

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:80",
    "http://localhost:8000", # Allow requests from frontend running on 8000 (if served directly)
    "http://localhost:8080" # Common port for local development
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
    # Assuming recommendations.json is in a sibling 'analysis' directory
    # So, if main.py is in 'implementation/', recommendations.json is in 'analysis/'
    current_dir = os.path.dirname(__file__)
    recommendations_file_path = os.path.join(current_dir, '..', 'analysis', 'recommendations.json')
    
    # In the Docker container:
    # main.py will be at /app/main.py
    # recommendations.json will be at /analysis/recommendations.json
    # So, relative path will be ../analysis/recommendations.json
    
    # Let's adjust for the Docker context if needed. Inside the container,
    # if main.py is in /app, and recommendations.json is in /analysis,
    # then the path will be /analysis/recommendations.json. Need to be absolute or relative from root.

    # The Dockerfile copies recommendations.json to /analysis/recommendations.json
    # So the app should read from there directly.
    container_recommendations_path = "/analysis/recommendations.json"

    try:
        with open(container_recommendations_path, "r") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Error: {container_recommendations_path} not found.")
        # Fallback for local testing outside Docker, if analysis is sibling
        try:
            with open(recommendations_file_path, "r") as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            return {"error": "recommendations.json not found"}
    except json.JSONDecodeError:
        return {"error": "Could not decode recommendations.json"}

