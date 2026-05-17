from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True, nullable = False)
    email = Column(String, unique = True, nullable = False)
    password = Column(String, nullable = True)
    auth_provider = Column(String, nullable = True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default= text('now()'))

class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(Integer, primary_key = True, nullable = False)
    name = Column(String, nullable = False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete = "CASCADE"), nullable = False)
    owner = relationship("User")

    __table_args__ = (
        UniqueConstraint("name", "owner_id", name="one_owner_unique_workspace"),
        )

class user_vault(Base):
    __tablename__ = "vault"

    id = Column(Integer, primary_key = True, nullable = False)
    platform = Column(String, nullable = False) 
    website_URL = Column(String,nullable = False)
    platform_username = Column(String, nullable = False)
    platform_password = Column(String, nullable = False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete = "CASCADE"), nullable= False)
    owner = relationship("User")
    workspace_id = Column(Integer, ForeignKey("workspaces.id", ondelete = "CASCADE"), nullable = True)
    workspace = relationship("Workspace")

    __table_args__ = (
        UniqueConstraint("platform", "owner_id","workspace_id", name="one_owner_one_platform_per_workspace"),
        )
    