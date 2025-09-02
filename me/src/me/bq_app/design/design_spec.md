# Full-Stack Application Design Specification

## 1. Overview

This document outlines the design for a full-stack application that displays BigQuery cost-saving recommendations. The application will consist of a Python FastAPI backend, a simple HTML/JavaScript frontend, and will be containerized using Docker Compose.

## 2. Backend Design (Python FastAPI)

The backend will be a simple FastAPI application responsible for serving the recommendations from a JSON file.

*   **Framework:** FastAPI
*   **Language:** Python 3.9+
*   **API Endpoint:** `/api/recommendations`
    *   **Method:** GET
    *   **Description:** Reads the `recommendations.json` file and returns its content as a JSON response.
    *   **Data Source:** `recommendations.json` file. **No database is required for this simple application.**

### Backend Directory Structure

```
backend/
├── app/
│   └── main.py
├── Dockerfile
├── recommendations.json
└── requirements.txt
```

### `main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:80",
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
    with open("recommendations.json") as f:
        data = json.load(f)
    return data
```

### `requirements.txt`

```
fastapi
uvicorn
```

### `Dockerfile` (for backend)

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 3. Frontend Design (HTML, CSS, JavaScript)

The frontend will be a single HTML page that fetches the recommendations from the backend API and displays them in a simple list.

*   **Frameworks/Libraries:** None (plain HTML, CSS, JavaScript)
*   **Functionality:**
    *   On page load, fetch data from the backend's `/api/recommendations` endpoint.
    *   Dynamically create and display a list of recommendations on the page.

### Frontend Directory Structure

```
frontend/
├── index.html
└── Dockerfile
```

### `index.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BigQuery Cost Recommendations</title>
    <style>
        body { font-family: sans-serif; margin: 2em; }
        h1 { color: #333; }
        ul { list-style-type: none; padding: 0; }
        li { background: #f4f4f4; margin: 5px 0; padding: 10px; border-radius: 5px; }
    </style>
</head>
<body>

    <h1>BigQuery Cost-Saving Recommendations</h1>
    <ul id="recommendations-list"></ul>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            fetch('http://localhost:8000/api/recommendations')
                .then(response => response.json())
                .then(data => {
                    const list = document.getElementById('recommendations-list');
                    data.forEach(item => {
                        const listItem = document.createElement('li');
                        listItem.textContent = item.recommendation;
                        list.appendChild(listItem);
                    });
                })
                .catch(error => console.error('Error fetching recommendations:', error));
        });
    </script>

</body>
</html>
```

### `Dockerfile` (for frontend)

```dockerfile
FROM nginx:alpine
COPY index.html /usr/share/nginx/html/
EXPOSE 80
```

## 4. Containerization (Docker Compose)

Docker Compose will be used to orchestrate the backend and frontend services.

### `docker-compose.yml`

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend/recommendations.json:/app/recommendations.json

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
```
