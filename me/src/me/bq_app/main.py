import asyncio
import logging
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from db import SessionLocal, engine, Base
from ingest import ingest_new_files
import models

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CACHE_DIR = '.bq_cache'

class CacheChangeHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            logger.info(f"Detected new file: {event.src_path}")
            ingest_new_files()

@app.on_event("startup")
async def startup_event():
    # Initial ingestion
    logger.info("Performing initial data ingestion...")
    ingest_new_files()
    logger.info("Initial ingestion complete.")

    # Start watching for file changes
    event_handler = CacheChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=f"{CACHE_DIR}/raw_queries", recursive=False)
    observer.schedule(event_handler, path=f"{CACHE_DIR}/raw_timelines", recursive=False)
    observer.start()
    logger.info(f"Started watching {CACHE_DIR} for changes.")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/queries")
def get_queries():
    db: Session = SessionLocal()
    queries = db.query(models.Query).all()
    db.close()
    return queries
