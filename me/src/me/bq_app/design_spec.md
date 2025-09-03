# Full-Stack Application Design Specification

This document outlines the design for a simple full-stack application to display recommendations from a JSON file.

## 1. Overview

The application will consist of a Python backend API, a static HTML/JavaScript frontend, and will be containerized using Docker Compose. The primary goal is to read a `recommendations.json` file and display its contents on a web page.

## 2. Backend Design (Python FastAPI)

The backend will be a lightweight API built using the FastAPI framework.

*   **Framework:** FastAPI
*   **Language:** Python 3.9+
*   **Dependencies:** `fastapi`, `uvicorn`

### API Endpoint

A single GET endpoint will be exposed:

*   **Endpoint:** `/api/recommendations`
*   **Method:** `GET`
*   **Description:** This endpoint will read the `recommendations.json` file from the filesystem and return its content as a JSON response.
*   **Data Storage:** No database is required. The `recommendations.json` file acts as the data source.
*   **Success Response (200 OK):**
    ```json
    {
      "recommendations": [
        {
          "id": 1,
          "service": "Compute Engine",
          "recommendation": "...",
          "priority": "High"
        }
      ]
    }
    ```

### Backend `main.py` (Example)

```python
from fastapi import FastAPI
import json

app = FastAPI()

@app.get("/api/recommendations")
def get_recommendations():
    # The JSON file will be mounted into the container at this path
    with open("/data/recommendations.json", "r") as f:
        data = json.load(f)
    return data
```

## 3. Frontend Design (HTML + JavaScript)

The frontend will be a single static `index.html` page that fetches and displays the data from the backend API.

*   **Frameworks:** None (vanilla HTML, CSS, and JavaScript)
*   **Structure:**
    *   `index.html`: The main HTML file.
    *   `style.css`: For basic styling.
    *   `script.js`: To fetch data from `/api/recommendations` and dynamically populate the page.

### UI Mockup

The UI will feature a simple heading and a table to display the recommendations.

*   **Title:** "Cloud Recommendations"
*   **Table Columns:** ID, Service, Recommendation, Priority

### Frontend `script.js` (Example)

```javascript

document.addEventListener("DOMContentLoaded", () => {
    fetch('/api/recommendations')
        .then(response => response.json())
        .then(data => {
            const tableBody = document.getElementById('recommendations-table-body');
            data.recommendations.forEach(rec => {
                let row = tableBody.insertRow();
                row.insertCell(0).innerText = rec.id;
                row.insertCell(1).innerText = rec.service;
                row.insertCell(2).innerText = rec.recommendation;
                row.insertCell(3).innerText = rec.priority;
            });
        })
        .catch(error => console.error('Error fetching recommendations:', error));
});
```

## 4. Containerization (Docker Compose)

The entire application will be managed using `docker-compose`.

*   **File:** `docker-compose.yml`
*   **Services:** `backend`, `frontend`

### `docker-compose.yml` Specification

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      # Mount the JSON file from the host into the container
      - ./analysis/recommendations.json:/data/recommendations.json:ro

  frontend:
    image: nginx:alpine
    ports:
      - "8080:80"
    volumes:
      # Mount the static frontend files
      - ./frontend:/usr/share/nginx/html:ro
      # Mount a custom nginx config to proxy API requests
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - backend
```

### NGINX Proxy Configuration (`nginx.conf`)

To avoid CORS issues and simplify API calls from the frontend, the NGINX server will act as a reverse proxy for the backend API.

```nginx
server {
    listen 80;

    location / {
        root   /usr/share/nginx/html;
        index  index.html index.htm;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000;
    }
}
```
