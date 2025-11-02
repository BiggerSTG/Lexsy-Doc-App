from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def create_app() -> FastAPI:
    app = FastAPI()

    # Enable CORS for frontend communication
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Import here to avoid circular imports at package import time
    from backend.api.routes import router
    app.include_router(router)

    return app


app = create_app()
