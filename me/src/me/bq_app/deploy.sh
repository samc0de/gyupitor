#!/bin/bash

# Navigate to the application directory
cd "$(dirname "$0")"

echo "Building and deploying the application using Docker Compose..."

# Build and run the Docker containers in detached mode
docker compose up --build -d

if [ $? -eq 0 ]; then
    echo "Application deployed successfully!"
    echo "Frontend accessible at http://localhost:80"
    echo "Backend accessible at http://localhost:8000"
else
    echo "Deployment failed. Please check the logs for errors."
fi
