from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api.routers import auth, requests
from app.security import get_secret


@asynccontextmanager
async def lifespan(app):
    get_secret()
    yield


app = FastAPI(title="SUSU HelpDesk", version="0.1.0", lifespan=lifespan)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(requests.router, prefix="/api/v1")


@app.exception_handler(SQLAlchemyError)
def database_error(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=503, content={"detail": "База данных временно недоступна"}
    )
