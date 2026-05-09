from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

def hash(password: str):
    return pwd_context.hash(password)

def match_password(hashed_password, password):
    return pwd_context.verify(password, hashed_password)