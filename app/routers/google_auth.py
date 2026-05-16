from fastapi import APIRouter, Depends, HTTPException, status, Request
from .. import google_oauth, models,oauth2
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from ..database import get_db
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

@router.get("/auth/google")
def google_login_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/auth/google/start")
def google_login():
    url = google_oauth.get_google_auth_url()
    return RedirectResponse(url = url)

@router.get("/auth/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    try:
        google_user =  await google_oauth.get_google_user_info(code)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to fetch user info from Google"
            )
    email = google_user.get("email")
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail = "Could not get email from Google")
    user = db.query(models.User).filter(models.User.email == email).first()

    if not user:
        user = models.User(
            email = email,
            password = None,
            auth_provider= "google"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = oauth2.create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}