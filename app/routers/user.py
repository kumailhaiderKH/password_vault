from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from .. import models, schemas, utils
from sqlalchemy.orm import Session
from ..database import engine, SessionLocal,get_db

router = APIRouter(
    prefix= '/users'
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def createuser(user: schemas.UserCreate, db:Session = Depends(get_db)):
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/")
def get_users(db:Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users



