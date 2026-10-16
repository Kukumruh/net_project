"""Apply migrations before serving the containerized API."""

import os

from alembic import command
from alembic.config import Config
from sqlalchemy import URL

# Local DATABASE_URL points at localhost:5433. Containers use the Compose network.
# URL.create also handles passwords containing URL-reserved characters.
os.environ["DATABASE_URL"] = URL.create(
    "postgresql+psycopg",
    username=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
    host="postgres",
    port=5432,
    database=os.environ["POSTGRES_DB"],
).render_as_string(hide_password=False)

from app.security import get_secret

get_secret()
command.upgrade(Config("alembic.ini"), "head")
os.execvp("uvicorn", ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"])
