from fastapi import APIRouter, Request, Form, Cookie, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from database import get_db  
from models import User
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
router = APIRouter(tags=["auth"])

@router.get("/login_page", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()
    if user and user.password == password:
        response = RedirectResponse(url="/profile", status_code=302)
        response.set_cookie(key="user", value=username)
        return response
    return templates.TemplateResponse("login.html", {
        "request": request,
        "message": "Неверный логин или пароль"
    })

@router.get("/profile", response_class=HTMLResponse)
def profile(
    request: Request,
    user: str = Cookie(default=None),
    db: Session = Depends(get_db)
):
    if not user:
        return RedirectResponse("/login_page")
    current_user = db.query(User).filter(User.username == user).first()
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "username": user,
        "user": current_user
    })

@router.get("/logout")
def logout():
    response = RedirectResponse("/login_page")
    response.delete_cookie("user")
    return response

@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register", response_class=HTMLResponse)
def register_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "message": "Пользователь уже существует"
        })
    new_user = User(username=username, password=password)
    db.add(new_user)
    db.commit()
    return templates.TemplateResponse("register.html", {
        "request": request,
        "message": "Регистрация прошла успешно!"
    })
