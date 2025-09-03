#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
IMAGE_NAME="bq-cost-app"
CONTAINER_NAME="bq-optimizer-container"
HOST_PORT="8000"

# Get the absolute path to the parent directory of this script.
# This ensures that the script can be run from anywhere.
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
PROJECT_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)

# Define absolute paths for the volumes based on the project root.
CACHE_DIR="$PROJECT_ROOT/../../.bq_cache"
DB_DIR="$PROJECT_ROOT/db_data"
DB_FILE="$DB_DIR/bq_analyzer.db"

# --- Pre-flight checks ---
# Create the database directory and file with open permissions if they don't exist.
echo "Checking for database directory at $DB_DIR..."
if [ ! -d "$DB_DIR" ]; then
    echo "Database directory not found. Creating..."
    mkdir -p "$DB_DIR"
    echo "Database directory created."
fi

echo "Checking for database file at $DB_FILE..."
if [ ! -f "$DB_FILE" ]; then
    echo "Database file not found. Creating and setting permissions..."
    sudo touch "$DB_FILE"
    sudo chmod 666 "$DB_FILE"
    echo "Database file created."
else
    echo "Database file found. Ensuring correct permissions..."
    sudo chmod 666 "$DB_FILE"
    echo "Permissions set."
fi

# --- Build Docker Image ---
echo "Building Docker image: $IMAGE_NAME..."
sudo docker build -t "$IMAGE_NAME" "$SCRIPT_DIR"

echo "Build complete."

# --- Run Docker Container ---
echo "Checking for and removing any existing container named $CONTAINER_NAME..."
if [ "$(sudo docker ps -q -f name=$CONTAINER_NAME)" ]; then
    sudo docker stop "$CONTAINER_NAME"
fi
if [ "$(sudo docker ps -aq -f status=exited -f name=$CONTAINER_NAME)" ]; then
    sudo docker rm "$CONTAINER_NAME"
fi

echo "Starting new container: $CONTAINER_NAME..."
sudo docker run -d \
    --name "$CONTAINER_NAME" \
    -p "$HOST_PORT:8000" \
    -v "$CACHE_DIR:/app/.bq_cache" \
    -v "$DB_DIR:/app/db_data" \
    "$IMAGE_NAME"

echo "Container is running."
echo "You can access the application at http://localhost:$HOST_PORT"
echo "To view logs, run: sudo docker logs -f $CONTAINER_NAME"
echo "To stop the container, run: sudo docker stop $CONTAINER_NAME"
