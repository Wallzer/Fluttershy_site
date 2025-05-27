
from sqlalchemy.orm import Session
from database import SessionLocal
import models

def create_admin(db: Session, username: str, password: str):
    existing_admin = db.query(models.User).filter(models.User.username == username).first()
    if existing_admin:
        print(f"Пользователь с логином {username} уже существует.")
        return

    # Создаём нового администратора с открытым паролем
    new_admin = models.User(username=username, password=password)
    db.add(new_admin)
    db.commit()
    print(f"Администратор {username} успешно создан!")

# Запускаем скрипт
if __name__ == "__main__":
    db = SessionLocal()
    create_admin(db, username="admin", password="adminpassword")  # Логин и пароль без шифрования
    db.close()
