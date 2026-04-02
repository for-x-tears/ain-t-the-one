

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app import models
from app.routers import tasks, auth, comments, system

# async 
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app = FastAPI(on_startup=[create_tables])
# разрешаю  запросы с любого origin, только для dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

routers = [auth.router, tasks.router, comments.router, system.router]
for router in routers:
    app.include_router(router)

@app.get("/")
async def root():
    return {"status": "ok"}