from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, status, HTTPException
from sqlalchemy.orm import Session
from . import schemas, database, models, config

oauth_scheme = OAuth2PasswordBearer(tokenUrl = 'login')



def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes = config.settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.settings.secret_key, algorithm=config.settings.algorithm)
    return encoded_jwt



def verify_access_token(token: str, credentials_exception):
    
    try:
        payload = jwt.decode(token, config.settings.secret_key, algorithms = [config.settings.algorithm])
        id: int = payload.get("user_id")

        if id == None:
            raise credentials_exception
        token_data = schemas.TokenData(id =id)
    except JWTError:
        raise credentials_exception
    return token_data

def get_current_user(token: str = Depends(oauth_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = f"Could not validate credentials", headers = {"WWW-Authenticate": "Bearer"})
    token = verify_access_token(token, credentials_exception)
    user = db.query(models.User).filter(models.User.id ==token.id).first()
    if user is None:
        raise credentials_exception
    return user

def create_verification_token(email:str):
    expire = datetime.utcnow()+ timedelta(hours = 24)
    data = {
        "email": email,
        "exp": expire,
        "token_type": "email_verify"
    }
    return jwt.encode(data, config.settings.secret_key, algorithm=config.settings.algorithm)

def verify_verification_token(token: str):
    try:
        payload  = jwt.decode(token, config.settings.secret_key, algorithms = [config.settings.algorithm])
        email = payload.get("email")
        token_type = payload.get("token_type")

        if email is None or token_type != "email_verify":
            return None
        return email
    except JWTError:
        return None






