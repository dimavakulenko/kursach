import databases
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import config

url = config.POSTGRES_DSN

engine = create_async_engine(url, echo=True)
database = databases.Database(url)