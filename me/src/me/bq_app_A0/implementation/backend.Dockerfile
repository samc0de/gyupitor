FROM python:3.9-slim

WORKDIR /app

COPY src/me/bq_app/implementation/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main application file
COPY src/me/bq_app/implementation/main.py ./main.py

# Copy the recommendations.json from the analysis directory
# This assumes the Docker build context is the root of the project
# If the build context is 'src/me/bq_app', then the path would be ../analysis/recommendations.json
# For now, let's assume the Dockerfile is in src/me/bq_app/implementation
# And the analysis folder is at src/me/bq_app/analysis
# So relative to WORKDIR /app in Docker, the path will be ../analysis/recommendations.json
# However, the Docker build context will be relative to the directory where the build command is run.
# If the build command is run from src/me/bq_app/implementation, then we need to go up two directories to reach bq_app, then down to analysis.
# Let's adjust the path for COPY to assume the build context is the project root.
# The design spec implies a structure like: backend/Dockerfile and recommendations.json at the same level as backend.
# Given the current setup, I need to copy the file from the original analysis directory.

# Assuming the Docker build context is set to the 'bq_app' directory for this to work correctly.
# If Docker build context is 'src/me/bq_app/', then the path is analysis/recommendations.json
# For now, I'll copy the file in a way that is compatible if the build context is the project root,
# and then the `main.py`'s logic handles the path at runtime.
# However, the Dockerfile should explicitly copy the file required by the app.

# Let's assume the Docker build context will be `src/me/bq_app`.
# So, from the build context, the path to main.py is `implementation/main.py`
# and the path to recommendations.json is `analysis/recommendations.json`.

# If `WORKDIR /app`, and main.py is at `/app/main.py`
# The main.py expects recommendations.json to be at `../analysis/recommendations.json` from its location.
# So, if main.py is in /app, then analysis should be in /analysis.
# Let's adjust copy commands to create this structure inside the container.

COPY src/me/bq_app/analysis/recommendations.json /analysis/recommendations.json

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
