from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, books, collections, dashboard, data_center, highlights, profile, review, settings as settings_routes, sync, tts, ai_chat
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="WeRead Review API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(dashboard.router)
    app.include_router(collections.router)
    app.include_router(data_center.router)
    app.include_router(auth.router)
    app.include_router(review.router)
    app.include_router(highlights.router)
    app.include_router(books.router)
    app.include_router(profile.router)
    app.include_router(settings_routes.router)
    app.include_router(sync.router)
    app.include_router(ai_chat.router)
    app.include_router(tts.router, prefix="/api/tts", tags=["tts"])

    return app


app = create_app()
