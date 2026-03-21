from fastapi import FastAPI
from app.database import engine, Base
from app import models
from app.routers import tasks, auth

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router)
app.include_router(tasks.router)

@app.get("/")
def root():
    return {"status": "ok"}