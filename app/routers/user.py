from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from .. import models, schemas, utils, oauth2, rate_limit as rl
from sqlalchemy.orm import Session
from ..database import engine, SessionLocal,get_db
from sqlalchemy.exc import IntegrityError

router = APIRouter(
    prefix= '/users'
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut, dependencies=[Depends(rl.rate_limit(limit=5, window=60))])
def createuser(user: schemas.UserCreate, db:Session = Depends(get_db)):
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    new_user = models.User(**user.model_dump())
    db.add(new_user)
    try:
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail = f"The user {user.email} already exists")
    return new_user


@router.get("/", response_model=list[schemas.UserOut], dependencies=[Depends(rl.rate_limit(limit=5, window=60))])
def get_users(db:Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users


@router.get("/{id}", response_model=schemas.UserOut, dependencies=[Depends(rl.rate_limit(limit=5, window=60))])
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"The user {id} does not exists")
    return user


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(rl.rate_limit(limit=5, window=60))])
def delete_user(id: int, db: Session = Depends(get_db)):
    user_query = db.query(models.User).filter(models.User.id == id)
    user = user_query.first()
    if user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"User {id} does not exist")
    user_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.UserOut, dependencies=[Depends(rl.rate_limit(limit=5, window=60))])
def update_user(id: int, updated_user: schemas.UserCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    user_query = db.query(models.User).filter(models.User.id == id)
    user = user_query.first()
    if user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"User {id} does not exist")
    if user.id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = f"Not authorized to perform requested action")
    hashed_password = utils.hash(updated_user.password)  # ✅ hash before saving
    updated_user.password = hashed_password
    try:
        user_query.update(updated_user.model_dump(), synchronize_session=False)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail = f"The user {user.email} already exists")
    return user_query.first()


