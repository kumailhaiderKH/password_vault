from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True, nullable = False)
    email = Column(String, unique = True, nullable = False)
    password = Column(String, nullable = False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default= text('now()'))

class user_vault(Base):
    __tablename__ = "vault"

    id = Column(Integer, primary_key = True, nullable = False)
    platform = Column(String, nullable = False) 
    website_URL = Column(String,nullable = False)
    platform_username = Column(String, nullable = False)
    platform_password = Column(String, nullable = False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete = "CASCADE"), nullable= False)
    owner = relationship("User")

   
    __table_args__ = (
        UniqueConstraint("platform", "owner_id", name="one_owner_one_platform"),
        )
    