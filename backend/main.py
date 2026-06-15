from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api.routes.analysis_routes import router as analysis_router
from app.api.routes.chatbot_routes import router as chatbot_router
from app.api.routes.history_routes import router as history_router
from app.api.routes.report_routes import router as report_router

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis_router, prefix=settings.API_PREFIX)
app.include_router(chatbot_router, prefix=settings.API_PREFIX)
app.include_router(history_router, prefix=settings.API_PREFIX)
app.include_router(report_router, prefix=settings.API_PREFIX)

settings.ensure_storage_dirs()
app.mount("/storage", StaticFiles(directory="storage"), name="storage")


@app.get("/")
def root():
    return {
        "message": "DeepShield AI Pro Backend is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "UP",
        "service": "DeepShield AI Pro"
    }
