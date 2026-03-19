"""FastAPI application entry point."""

from fastapi import FastAPI

app = FastAPI(
    title="uSipipo Backend API",
    description="Backend API principal del ecosistema uSipipo",
    version="0.1.0",
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to uSipipo Backend API"}
