from passlib.context import CryptContext
from cryptography.fernet import Fernet
from .config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

def get_key_by_version(version: int) -> str:
    print(f"looking for version: {version}")
    keys = {
        1: settings.encryption_key_1,
        2: settings.encryption_key_2,
        3: settings.encryption_key_3,
    }
    return keys.get(version)



def hash(password: str):
    return pwd_context.hash(password)

def encrypt_password(password: str) -> str:
    key = get_key_by_version(settings.current_key_version)
    f = Fernet(key)
    return f.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password: str, key_version: int) -> str:
    key = get_key_by_version(key_version)
    f = Fernet(key)
    return f.decrypt(encrypted_password.encode()).decode()

def match_password(hashed_password, password):
    return pwd_context.verify(password, hashed_password)
