import uvicorn

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.database import database
from app.config import config
from app.routers import executor, customer

app = FastAPI(
    title=config.APP_NAME
)

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(executor.router)
app.include_router(customer.router)


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.on_event("startup")
async def startup():
    await database.connect()


if __name__ == '__main__':
    uvicorn.run('main:app', host='127.0.0.1', port=5000, log_level='debug', reload=True, use_colors=True)
