import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .database import engine, Base, SessionLocal
from .routers import auth, centers, batches, students, sync, reports, leaves
from .production_seed import seed_production_db

# Create all database tables on startup
Base.metadata.create_all(bind=engine)

# Auto-seed if database is empty
db_session = SessionLocal()
try:
    seed_production_db(db_session)
finally:
    db_session.close()

app = FastAPI(
    title="NGO Attendance Management Portal",
    description="A local attendance system with role dashboards, CSV syncing, and PDF analysis.",
    version="1.0.0"
)

# CORS middleware for local testing/access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(centers.router)
app.include_router(batches.router)
app.include_router(students.router)
app.include_router(sync.router)
app.include_router(reports.router)
app.include_router(leaves.router)

# Define static files directory
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

# Ensure static folder exists
os.makedirs(STATIC_DIR, exist_ok=True)

# Mount the static directory to serve HTML/JS/CSS assets
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def read_root():
    """
    Serves the main frontend Single Page Application (SPA) on root path.
    """
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {
        "status": "online",
        "message": "FastAPI Server is running. Frontend static/index.html is not created yet."
    }

@app.get("/health")
def healthcheck():
    return {"status": "healthy"}
