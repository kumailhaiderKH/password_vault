from fastapi import APIRouter, HTTPException, status, Depends, Response
from .. import schemas, database, models, oauth2, utils, rate_limit as rl
from sqlalchemy.orm import Session
from ..database import engine, SessionLocal, get_db
from sqlalchemy.exc import IntegrityError

router = APIRouter()

@router.post("/vault", status_code=status.HTTP_201_CREATED,response_model=schemas.password_out, dependencies=[Depends(rl.rate_limit(limit=5, window=60))])
def save_password(vault_entry: schemas.add_password, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    if vault_entry.workspace_id:
        workspace = db.query(models.Workspace).filter(models.Workspace.id == vault_entry.workspace_id, models.Workspace.owner_id == current_user.id).first()
        if workspace is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workspace {vault_entry.workspace_id} does not exist"
            )
    encrypted_password = utils.encrypt_password(vault_entry.platform_password)
    vault_entry.platform_password = encrypted_password
    new_entry = models.user_vault(
        owner_id = current_user.id,
        **vault_entry.model_dump()
        )
    db.add(new_entry)
    try:
        db.commit()
        db.refresh(new_entry)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail = f"You already have a password saved for {vault_entry.platform}")
    new_entry.platform_password = utils.decrypt_password(new_entry.platform_password)
    return new_entry


@router.get("/vault",response_model=list[schemas.password_out], dependencies=[Depends(rl.rate_limit(limit=5, window=60))])
def get_passwords(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    passwords = db.query(models.user_vault).filter(models.user_vault.owner_id==current_user.id).all()
    for password in passwords:
        password.platform_password = utils.decrypt_password(password.platform_password)
    return passwords

@router.delete("/vault/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(rl.rate_limit(limit=5, window=60))])
def delete_password(id: int, db:Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    entry_query = db.query(models.user_vault).filter(models.user_vault.id == id)
    entry = entry_query.first()
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"Vault id {id} does not exist")
    if entry.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = f"Not authorized to perform requested action")
    entry_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/vault/{id}", response_model=schemas.password_out, dependencies=[Depends(rl.rate_limit(limit=5, window=60))])
def update_password(id: int, updated_entry: schemas.add_password, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    entry_query = db.query(models.user_vault).filter(models.user_vault.id == id)
    entry = entry_query.first()
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"Vault id {id} does not exist")
    if entry.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = f"Not authorized to perform requested action")
    if updated_entry.workspace_id:
        workspace = db.query(models.Workspace).filter(models.Workspace.id == updated_entry.workspace_id, models.Workspace.owner_id == current_user.id).first()
        if workspace is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workspace {updated_entry.workspace_id} does not exist"
            )
    encrypted_password = utils.encrypt_password(updated_entry.platform_password)
    updated_entry.platform_password = encrypted_password
    try:
        entry_query.update(updated_entry.model_dump(), synchronize_session=False)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail = f"You already have a password saved for {updated_entry.platform}")
    updated = entry_query.first()
    updated.platform_password = utils.decrypt_password(updated.platform_password)
    return updated 
