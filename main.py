from fastapi import FastAPI, Request, Form, Depends, Cookie,HTTPException,Request
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import Column, Integer, String
from database import Base, SessionLocal, engine
from routers import auth, projects
import models

# Создание таблиц
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Подключение статики и шаблонов
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Модель пользователя


# Получение сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Главная страница
@app.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db), user: str = Cookie(default=None)):
    current_user = db.query(models.User).filter(models.User.username == user).first() if user else None
    projects = db.query(models.Project).all()  # пример модели Project
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": current_user,
        "projects": projects
    })

# Включение роутеров
app.include_router(projects.router)
app.include_router(auth.router)



@app.get("/create_note", response_class=HTMLResponse)
def add_project_page(
    request: Request, 
    user: str = Cookie(default=None), 
    db: Session = Depends(get_db)
):
    if not user:
        return RedirectResponse("/login_page")
    
    current_user = db.query(models.User).filter(models.User.username == user).first()
    
    if not current_user or current_user.username != "admin":
        return RedirectResponse("/")
    
    return templates.TemplateResponse("add_project.html", {"request": request})

@app.post("/create_note")
def add_project(title: str = Form(...), description: str = Form(...), db: Session = Depends(get_db)):
    new_project = models.Project(title=title, description=description)
    db.add(new_project)
    db.commit()
    return RedirectResponse("/", status_code=302)    


@app.get("/delete_project_page", response_class=HTMLResponse)
def delete_project_page(
    request: Request,
    db: Session = Depends(get_db)
):
    projects = db.query(models.Project).all()
    return templates.TemplateResponse("delete_project.html", {
        "request": request,
        "projects": projects,
        "message": ""
    })


@app.post("/delete_project", response_class=HTMLResponse)
def delete_project_route(
    request: Request,
    project_id: int = Form(...),
    db: Session = Depends(get_db)
):
    project = db.query(models.Project).get(project_id)
    if not project:
        projects = db.query(models.Project).all()
        return templates.TemplateResponse("delete_project.html", {
            "request": request,
            "projects": projects,
            "message": "Проект не найден"
        })
    db.query(models.Comment)\
      .filter(models.Comment.project_id == project_id)\
      .delete(synchronize_session=False)

    db.delete(project)
    db.commit()

    projects = db.query(models.Project).all()
    return templates.TemplateResponse("delete_project.html", {
        "request": request,
        "projects": projects,
        "message": "Проект и его комментарии успешно удалены"
    })

@app.get("/about", response_class=HTMLResponse)
def about_page(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/note/{note_id}", response_class=HTMLResponse)
async def read_note(request: Request, note_id: int, db: Session = Depends(get_db),user: str = Cookie(default=None)):
    project = db.query(models.Project).filter(models.Project.id == note_id).first()
    if not project:
        return HTMLResponse(status_code=404, content="Not Found")

    # Получаем все комментарии к проекту
    comments = db.query(models.Comment).filter(models.Comment.project_id == note_id).all()
    current_user = db.query(models.User).filter(models.User.username == user).first() if user else None
    return templates.TemplateResponse("note.html", {
        "request": request,
        "project": project,
        "comments": comments,
        "user": current_user,
        "note_id": note_id
        
    })

@app.post("/note/{note_id}/comment")
def add_comment(
    note_id: int,
    request: Request,
    content: str = Form(...),
    user: str = Cookie(default=None),
    db: Session = Depends(get_db),
):
    # Если в куках нет user — отправляем на логин
    if not user:
        return RedirectResponse("/login_page", status_code=303)

    # Ищем в БД пользователя по username из куки
    current_user = db.query(models.User).filter(models.User.username == user).first()
    if not current_user:
        # кука есть, а пользователя нет в БД — принудительный логин
        return RedirectResponse("/login_page", status_code=303)

    # Проект должен существовать
    project = db.query(models.Project).get(note_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Создаём комментарий, привязан к project_id и user_id
    comment = models.Comment(
        content=content,
        project_id=note_id,
        user_id=current_user.id
    )
    db.add(comment)
    db.commit()

    # После POST — редирект обратно на страницу проекта
    return RedirectResponse(f"/note/{note_id}", status_code=303)
