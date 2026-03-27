from fastapi import FastAPI
from app.database import engine, Base
from app import models
from app.routers import tasks, auth, comments

Base.metadata.create_all(bind=engine)

app = FastAPI()

routers = [auth.router, tasks.router, comments.router]
for router in routers:
    app.include_router(router)

@app.get("/")
def root():
    return {"status": "ok"}