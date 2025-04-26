from fastapi import APIRouter, Request, Depends, Form, status, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from . import models, schemas, crud, auth
from .database import SessionLocal
from fastapi.templating import Jinja2Templates



router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/login")

@router.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register", response_class=HTMLResponse)
def register(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    if crud.get_user_by_username(db, username=username):
        return RedirectResponse(url="/register", status_code=status.HTTP_302_FOUND)
    crud.create_user(db, schemas.UserCreate(username=username, password=password))
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login", response_class=HTMLResponse)
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    access_token = auth.manager.create_access_token(data={"sub": user.username})
    response = RedirectResponse(url="/notes", status_code=status.HTTP_302_FOUND)
    auth.manager.set_cookie(response, access_token)
    return response

@router.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(auth.manager.cookie_name)
    return response

@router.get("/notes", response_class=HTMLResponse)
def read_notes(request: Request, user=Depends(auth.manager)):
    db = SessionLocal()
    notes = crud.get_notes(db=db, user_id=user.id)
    return templates.TemplateResponse("notes.html", {"request": request, "notes": notes})

@router.get("/create-note", response_class=HTMLResponse)
def create_note_form(request: Request, user=Depends(auth.manager)):
    return templates.TemplateResponse("create_note.html", {"request": request})

@router.post("/notes", response_class=HTMLResponse)
def create_note(request: Request, title: str = Form(...), content: str = Form(...), user=Depends(auth.manager)):
    db = SessionLocal()
    crud.create_note(db, schemas.NoteCreate(title=title, content=content), user.id)
    return RedirectResponse(url="/notes", status_code=status.HTTP_302_FOUND)

