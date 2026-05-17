from fastapi import APIRouter, HTTPException, status, Depends, Response
from .. import schemas, database, oauth2, models
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


router = APIRouter()

@router.post("/workspaces", status_code=status.HTTP_201_CREATED, response_model=schemas.workspace_out)
def create_workspace(workspace: schemas.workspace_create, db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user)):
    new_entry = models.Workspace(owner_id = current_user.id, **workspace.model_dump())
    db.add(new_entry)
    try:
        db.commit()
        db.refresh(new_entry)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail = f"User {current_user.id} has already a workspace named {workspace.name}")
    return new_entry

@router.get("/workspaces", response_model=list[schemas.workspace_out])
def get_workspaces(db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user)):
    entries = db.query(models.Workspace).filter(models.Workspace.owner_id == current_user.id).all()
    return entries

@router.delete("/workspaces/{id}")
def delete_worspace(id: int, db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user)):
    entry_query = db.query(models.Workspace).filter(models.Workspace.id == id)
    entry = entry_query.first()
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"Workspace {id} does not exist")
    if entry.owner_id != current_user.id :
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = f"Not authorized to perform requested action")
    entry_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
    
    



