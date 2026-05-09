from fastapi import FastAPI
from .database import engine
from . import models
from .routers import user, auth, password_vault

models.Base.metadata.create_all(bind = engine)

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World!!!"}

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(password_vault.router)
