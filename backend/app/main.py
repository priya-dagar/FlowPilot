from fastapi import FastAPI

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