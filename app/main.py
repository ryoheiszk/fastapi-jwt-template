from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.router import router as api_v1_router

app = FastAPI(
    title="FastAPI JWT Sample",
    description="FastAPI sample with JWT authentication",
    version="0.1.0",
    docs_url=f"{settings.BASE_URL}/docs",
    redoc_url=f"{settings.BASE_URL}/redoc",
    openapi_url=f"{settings.BASE_URL}/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router, prefix=f"{settings.BASE_URL}/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
