from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas, database, models, utils, oauth2, rate_limit as rl

from fastapi.security.oauth2 import OAuth2PasswordRequestForm

router = APIRouter()

@router.post("/login", dependencies=[Depends(rl.rate_limit(limit=5, window=60))])
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email  == user_credentials.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = f"Invalid Credntials")
    if not utils.match_password(user.password, user_credentials.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = f"Invalid Credntials")
    access_token= oauth2.create_access_token(data = {"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}