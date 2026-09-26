# from sqlalchemy import text
#
# from app.database import engine
#
#
# def test_connection():
#     with engine.connect() as connection:
#         result = connection.execute(text("SELECT version()"))
#         print(result.scalar())
#
#
# if __name__ == "__main__":
#     test_connection()

from app.database import Base
from app import models


if __name__ == "__main__":
    for table in Base.metadata.sorted_tables:
        print(table.name)