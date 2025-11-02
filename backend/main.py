"""Entrypoint for running the backend FastAPI app.

Run with: python -m backend.main or using uvicorn:
    uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
"""

from backend.app import app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)