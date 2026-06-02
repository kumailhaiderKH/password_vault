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

@router.post("/vault/{id}/share", response_model=schemas.share_password_out)
def share_password(id: int, shared_entry: schemas.share_password, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    new_entry = db.query(models.user_vault).filter(models.user_vault.id == id).first()
    shared_user = db.query(models.User).filter(models.User.id == shared_entry.shared_with).first()
    if new_entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"vault id {id} does not exist")
    if shared_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"The user {shared_entry.shared_with} does not exist")
    if new_entry.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = f"The vault id {new_entry.id} is not yours to share")
    if shared_entry.shared_with == current_user.id:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail = "You cannot share password. with yourself")
    
    new_shared_entry = models.shared_password(owner_id = current_user.id,vault_id = id, **shared_entry.model_dump())
    db.add(new_shared_entry)
    try:
        db.commit()
        db.refresh(new_shared_entry)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail = f"You already have shared this password with {shared_user.id}")
    new_shared_entry.vault.platform_password = utils.decrypt_password(new_shared_entry.vault.platform_password)
    return new_shared_entry

@router.get("/vault/shared", response_model=list[schemas.share_password_out])
def get_shared_passwords(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    shared_entries = db.query(models.shared_password).filter(models.shared_password.shared_with == current_user.id).all()
    for shared_entry in shared_entries:
        shared_entry.vault.platform_password = utils.decrypt_password(shared_entry.vault.platform_password)
    return shared_entries

@router.delete("/vault/{id}/share/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shared_password(id: int, user_id: int, db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    vault = db.query(models.user_vault).filter(models.user_vault.id == id).first()
    user = db.query(models.User).filter(models.User.id == user_id).first()
    entry = db.query(models.shared_password).filter(models.shared_password.vault_id == id, models.shared_password.shared_with == user_id).first()
    if vault is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"Vault id {id} does not exist")
    if user is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f"User {user_id} does not exist")
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"Vault {id} has not been shared with user {user_id}")
    if entry.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = f"You do not have permission to perform this task")
    db.delete(entry)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


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
