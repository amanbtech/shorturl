from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_database
from routes.auth_routes import router as auth_router
from routes.url_routes import router as url_router
from scheduler import start_scheduler
app = FastAPI(
    title="URL Shortener API",
    description="Scalable URL Shortener using FastAPI, SQLite and Redis",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
init_database()
app.include_router(auth_router)
app.include_router(url_router)
@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "service": "URL Shortener"
    }
@app.on_event("startup")
def startup():
    start_scheduler()