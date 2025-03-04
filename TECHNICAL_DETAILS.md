# Технические детали проекта

## Модели данных (models.py)

### User
- Поля: id, name, email, password, created_at, order_counter
- Связи: orders, cancelled_items
- Особенности: счетчик для пользовательских ID заказов

### Order
- Поля: id, user_id, user_order_id, client_name, status, total_amount, created_at, updated_at
- Связи: items (OrderItem)
- Статусы: ACTIVE, COMPLETED, CANCELLED
- Свойства: status_display, status_color

### OrderItem
- Поля: id, order_id, product_name, quantity, price, created_at
- Связи: order
- Свойства: subtotal

### CancelledItem
- Поля: id, user_id, product_name, quantity, price, order_reference, cancelled_at
- Связи: user
- Свойства: subtotal

## Основные маршруты (app.py)

### Аутентификация
- `/login` - вход в систему
- `/register` - регистрация
- `/logout` - выход

### Заказы
- `/orders` - список заказов с фильтрацией и пагинацией
- `/orders/create` - создание заказа
- `/orders/<id>` - просмотр заказа
- `/orders/<id>/edit` - редактирование заказа
- `/orders/<id>/complete` - завершение заказа
- `/orders/<id>/cancel` - отмена заказа
- `/orders/batch/complete` - пакетное завершение заказов
- `/orders/batch/cancel` - пакетное отмена заказов
- `/orders/cleanup` - удаление отмененных заказов

### Прочее
- `/profile` - профиль пользователя
- `/cancelled-items` - список отмененных товаров
- `/toggle_theme` - переключение темы

## Особенности реализации

### Темы оформления
- Светлая тема: `light-theme.css`
- Темная тема: `dark-theme.css`
- Переключение через сессию: `session['dark_mode']`

### Email-уведомления
- Настройка через переменные окружения в `.env`
- Отправка при завершении заказа

### Пользовательские ID заказов
- Каждый пользователь имеет свою нумерацию заказов
- Счетчик хранится в модели User

### Отмененные товары
- При отмене заказа товары сохраняются в отдельной таблице
- Сохраняется ссылка на номер заказа

## Скрипты

### start_app.bat
```
@echo off
chcp 65001 > nul
cd %~dp0
call venv\Scripts\activate.bat
echo Запуск Order Management System...
set FLASK_DEBUG=1
set FLASK_ENV=development
start http://127.0.0.1:5000
python -m flask run --debug
pause
```

### setup.bat
Скрипт для первоначальной настройки:
- Создание виртуального окружения
- Установка зависимостей
- Инициализация базы данных 