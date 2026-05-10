from fastapi import APIRouter, HTTPException, status, Depends
from .. import schemas, database, models, oauth2, utils
from sqlalchemy.orm import Session
from ..database import engine, SessionLocal, get_db
from sqlalchemy.exc import IntegrityError

router = APIRouter()

@router.post("/vault", status_code=status.HTTP_201_CREATED,response_model=schemas.password_out)
def save_password(vault_entry: schemas.add_password, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    hashed_password = utils.hash(vault_entry.platform_password)
    vault_entry.platform_password = hashed_password
    new_entry = models.user_vault(
        owner_id = current_user.id,
        **vault_entry.dict()
        )
    db.add(new_entry)
    try:
        db.commit()
        db.refresh(new_entry)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail = f"You already have a password saved for {vault_entry.platform}")
    return new_entry


@router.get("/vault",response_model=list[schemas.password_out])
def get_passwords(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    passwords = db.query(models.user_vault).filter(models.user_vault.owner_id==current_user.id).all()
    return passwords