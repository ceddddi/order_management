from contextlib import contextmanager
from typing import Generator, Any
import logging
from werkzeug.security import generate_password_hash

# Импортируем db из models.py вместо создания нового экземпляра
from models import db

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@contextmanager
def db_session() -> Generator[Any, None, None]:
    """
    Контекстный менеджер для работы с сессией базы данных.
    Автоматически выполняет commit при успешном выполнении
    и rollback при возникновении исключения.
    """
    try:
        yield db.session
        db.session.commit()
        logger.debug("Database transaction committed successfully")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Database transaction rolled back due to error: {str(e)}")
        raise
    finally:
        db.session.close()
        logger.debug("Database session closed")

def init_db(app: Any) -> None:
    """
    Инициализирует базу данных с приложением Flask.
    
    Args:
        app: Экземпляр приложения Flask
    """
    db.init_app(app)
    with app.app_context():
        # Импортируем модели здесь, чтобы избежать циклических импортов
        from models import User
        
        # Создаем все таблицы
        db.create_all()
        logger.info("Database initialized successfully")

        # Проверяем, есть ли уже администратор
        admin = User.query.filter_by(email='admin@example.com').first()
        if not admin:
            admin = User(
                name='Admin',
                email='admin@example.com',
                password=generate_password_hash('admin123')
            )
            db.session.add(admin)
            db.session.commit()
            logger.info("Создан пользователь admin@example.com с паролем admin123")

if __name__ == '__main__':
    # Для запуска инициализации напрямую
    from flask import Flask
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///new_order_management.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    init_db(app) 