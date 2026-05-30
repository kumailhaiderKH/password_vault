from fastapi import FastAPI
from .database import engine
from . import models
from .routers import user, auth, password_vault, google_auth, workspace
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles


templates = Jinja2Templates(directory="app/templates")

#models.Base.metadata.create_all(bind = engine)

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello Worlds!!!"}

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(password_vault.router)
app.include_router(google_auth.router)
app.include_router(workspace.router)