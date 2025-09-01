# BigQuery Cost Optimization Application

This repository contains the initial implementation of the BigQuery Cost Optimization application, which includes a FastAPI backend and a basic web UI.

## Project Structure

-   `backend/`: Contains the FastAPI application.
-   `frontend/`: Contains the static HTML, CSS, and JavaScript for the web UI.

## Getting Started

To run this application locally using Docker, follow these steps:

### Prerequisites

-   Docker and Docker Compose installed.

### 1. Build and Run the Backend

Navigate to the `backend` directory and build/run the Docker image:

```bash
cd backend
docker build -t bq-optimizer-backend .
docker run -d --name bq-optimizer-backend -p 8000:8000 bq-optimizer-backend
```

The backend API will be accessible at `http://localhost:8000`.

### 2. Build and Run the Frontend

Navigate to the `frontend` directory and build/run the Docker image:

```bash
cd frontend
docker build -t bq-optimizer-frontend .
docker run -d --name bq-optimizer-frontend -p 3000:80 bq-optimizer-frontend
```

The frontend application will be accessible at `http://localhost:3000`.

### 3. Access the Application

Open your web browser and go to `http://localhost:3000` to view the application.

## Status Update

### Completed:
-   **Project Structure**: Initial directories (`backend/`, `frontend/`) are set up.
-   **FastAPI Backend**: Basic FastAPI application with a mock `/recommendations` endpoint is implemented. It provides a list of sample optimization recommendations.
-   **Initial UI Components**: A simple HTML/CSS/JS frontend is created, demonstrating the core UI style guide (colors, typography, basic components like cards, buttons, tags). A simplified dashboard view is presented, showing how mock recommendation data could be displayed.
-   **Dockerization**: `Dockerfile`s for both the backend and frontend are provided for easy containerization and local execution.

### Next Steps:
-   Refine UI components and implement more detailed views (e.g., Recommendation Detail).
-   Integrate frontend with backend API calls.
-   Implement persistent storage for recommendations (e.g., connect to PostgreSQL).
-   Develop the Analyzer service to fetch and process BigQuery job data.
