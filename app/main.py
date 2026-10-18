import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api.routers import auth, requests
from app.security import get_secret


@asynccontextmanager
async def lifespan(app):
    get_secret()
    yield


app = FastAPI(title="SUSU HelpDesk", version="0.1.0", lifespan=lifespan)

# Comma-separated frontend origins; set the deployed frontend origin in production.
cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(requests.router, prefix="/api/v1")


@app.exception_handler(SQLAlchemyError)
def database_error(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=503, content={"detail": "База данных временно недоступна"}
    )
