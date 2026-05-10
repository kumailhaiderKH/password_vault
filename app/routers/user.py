from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from .. import models, schemas, utils
from sqlalchemy.orm import Session
from ..database import engine, SessionLocal,get_db
from sqlalchemy.exc import IntegrityError

router = APIRouter(
    prefix= '/users'
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def createuser(user: schemas.UserCreate, db:Session = Depends(get_db)):
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    new_user = models.User(**user.dict())
    db.add(new_user)
    try:
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail = f"The user {user.email} already exists")
    return new_user

@router.get("/", response_model=list[schemas.UserOut])
def get_users(db:Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users


