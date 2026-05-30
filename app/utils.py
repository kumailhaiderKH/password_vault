from passlib.context import CryptContext
from cryptography.fernet import Fernet
from .config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

def hash(password: str):
    return pwd_context.hash(password)

def encrypt_password(password: str) -> str:
    f = Fernet(settings.encryption_key)
    return f.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password: str) -> str:
    f = Fernet(settings.encryption_key)
    return f.decrypt(encrypted_password.encode()).decode()

def match_password(hashed_password, password):
    return pwd_context.verify(password, hashed_password)