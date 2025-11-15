"""FastAPI application entry point."""
from fastapi import FastAPI
from api.routers import insights, signals, sources

app = FastAPI(title="QuietlyStated API", version="1.0.0")

app.include_router(insights.router, prefix="/insights", tags=["insights"])
app.include_router(signals.router, prefix="/signals", tags=["signals"])
app.include_router(sources.router, prefix="/sources", tags=["sources"])


@app.get("/")
def root():
    """Root endpoint."""
    return {"message": "QuietlyStated API", "version": "1.0.0"}

