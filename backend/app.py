from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router


def create_app() -> FastAPI:
    app = FastAPI()

    # Enable CORS for frontend communication
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://main.d2dczcrek6651z.amplifyapp.com/"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)

    return app


app = create_app()
