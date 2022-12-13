from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app import app_settings

app = FastAPI(
    openapi_url=f"{app_settings.docs_prefix}/openapi.json",
    docs_url=f"{app_settings.docs_prefix}/docs",
    redoc_url=f"{app_settings.docs_prefix}/redoc",
)


origins = [
    "http:localhost:8000",
    "http:localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.add_middleware()

@app.get("/", tags=["Root"])
async def read_root():
    return {
        "message": "Please go to /api/docs endpoint to see the API documentation."
    }