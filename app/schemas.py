from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime



class UserCreate(BaseModel):
    email: EmailStr
    password: str

class add_password(BaseModel):
    platform: str
    website_URL: str
    platform_username: str
    platform_password: str

class TokenData(BaseModel):
    id: Optional[int] = None




