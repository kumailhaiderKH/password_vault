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
    is_verified: bool
    class Config:
        from_attributes = True

class workspace_create(BaseModel):
    name: str
    class Config:
        from_attributes = True

class workspace_out(BaseModel):
    id:int
    name: str
    class Config:
        from_attributes = True

class add_password(BaseModel):
    platform: str
    website_URL: str
    platform_username: str
    platform_password: str
    workspace_id: Optional[int] = None
    class Config:
        from_attributes = True

class password_out(BaseModel):
    id: int
    platform: str
    website_URL: str
    platform_username: str
    platform_password: str
    workspace: Optional[workspace_out] = None
    class Config:
        from_attributes = True

class share_password(BaseModel):
    shared_with: int
    permission: Optional[str] = "view"

    class Config:
        from_attributes = True

class share_password_out(BaseModel):
    id: int
    owner: UserOut
    shared_with: int
    permission: Optional[str]
    vault: password_out
    class Config:
        from_attributes = True
    

class TokenData(BaseModel):
    id: Optional[int] = None




