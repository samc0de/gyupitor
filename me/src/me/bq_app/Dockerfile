# Stage 1: Build the React frontend
FROM node:18-slim as frontend-builder

WORKDIR /app/frontend

# Copy package.json and package-lock.json (if available)
COPY frontend/package.json ./
# If you have a package-lock.json, it's good practice to copy it too
# COPY frontend/package-lock.json ./

# Install dependencies
RUN npm install

# Copy the rest of the frontend source code
COPY frontend/ .

# Build the static files
RUN npm run build

# Stage 2: Build the final Python application
FROM python:3.11-slim

WORKDIR /app

# Install backend dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend application code
COPY backend/ ./backend

# Copy the built frontend static files from the builder stage
COPY --from=frontend-builder /app/frontend/build ./static

# Copy the startup script
COPY start.sh .
RUN chmod +x ./start.sh

# Expose the port the app runs on
EXPOSE 8000

# Set the entrypoint to the startup script
ENTRYPOINT ["./start.sh"]