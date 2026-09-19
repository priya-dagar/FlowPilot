from fastapi import FastAPI
from .database import engine, Base
from . import models
from .routes import requests as requests_router
from .routes import approvals as approvals_router
from fastapi.middleware.cors import CORSMiddleware





Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="FlowPilot",
    description="Agentic Enterprise Process Automation",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": "FlowPilot API is running",
        "status": "healthy"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(requests_router.router)
app.include_router(approvals_router.router)
