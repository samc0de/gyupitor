# Stage 1: Prepare the frontend static assets
FROM nginx:alpine AS frontend
WORKDIR /usr/share/nginx/html
COPY frontend/ ./

# Stage 2: Build the backend and serve the frontend
FROM python:3.10-slim-buster AS backend
WORKDIR /app
COPY --from=frontend /usr/share/nginx/html /app/static
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
