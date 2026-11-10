"""Minimal FastAPI application for the CareerHub project.

- Provides a root endpoint (`/`) that returns a simple greeting.
- FastAPI automatically generates OpenAPI docs at `/docs`.
"""

from fastapi import FastAPI

app = FastAPI(title="CareerHub API", version="0.1.0")

@app.get("/")
def read_root():
    """Root endpoint – returns a welcome message.
    """
    return {"message": "Welcome to CareerHub!"}

# Example additional endpoint (optional)
@app.get("/ping")
def ping():
    """Simple health‑check endpoint.
    """
    return {"ping": "pong"}
