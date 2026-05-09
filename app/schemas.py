from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime



class UserCreate(BaseModel):
    email: EmailStr
    password: str
    class Config:
        from_attributes = True

class UserOut(BaseModel):
    id : int
    email: EmailStr
    created_at: datetime
    class Config:
        from_attributes = True

class add_password(BaseModel):
    platform: str
    website_URL: str
    platform_username: str
    platform_password: str
    class Config:
        from_attributes = True

class password_out(BaseModel):
    id: int
    platform: str
    website_URL: str
    platform_username: str
    owner: UserOut
    class Config:
        from_attributes = True
class TokenData(BaseModel):
    id: Optional[int] = None




