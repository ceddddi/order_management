import pytest
from app import app, db
from models import User, Order, OrderItem, OrderStatus
from werkzeug.security import generate_password_hash
import json
from datetime import datetime

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Создаем тестового пользователя
            test_user = User(
                name='Test User',
                email='test@example.com',
                password=generate_password_hash('password123')
            )
            db.session.add(test_user)
            db.session.commit()
            
            # Создаем тестовый заказ
            test_order = Order(
                user_id=test_user.id,
                user_order_id=1,
                client_name='Test Client',
                total_amount=100.0,
                status=OrderStatus.ACTIVE
            )
            db.session.add(test_order)
            db.session.commit()
            
            # Добавляем товар в заказ
            test_item = OrderItem(
                order_id=test_order.id,
                product_name='Test Product',
                quantity=2,
                price=50.0
            )
            db.session.add(test_item)
            db.session.commit()
            
        yield client
        
        with app.app_context():
            db.drop_all()

def login(client, email, password):
    return client.post('/login', data=dict(
        email=email,
        password=password
    ), follow_redirects=True)

def logout(client):
    return client.get('/logout', follow_redirects=True)

def test_login_logout(client):
    """Тест авторизации и выхода из системы"""
    # Проверяем успешный вход
    response = login(client, 'test@example.com', 'password123')
    assert b'Welcome' in response.data or b'Dashboard' in response.data
    
    # Проверяем успешный выход
    response = logout(client)
    assert b'Login' in response.data

def test_create_order(client):
    """Тест создания заказа"""
    # Сначала авторизуемся
    login(client, 'test@example.com', 'password123')
    
    # Создаем заказ
    response = client.post('/orders/create', data={
        'client_name': 'New Client',
        'product_name_0': 'Product 1',
        'quantity_0': '3',
        'price_0': '25.5',
        'product_name_1': 'Product 2',
        'quantity_1': '1',
        'price_1': '50.0'
    }, follow_redirects=True)
    
    assert b'successfully created' in response.data or b'успешно создан' in response.data
    
    # Проверяем, что заказ действительно создан в базе
    with app.app_context():
        order = Order.query.filter_by(client_name='New Client').first()
        assert order is not None
        assert order.total_amount == 126.5  # 3 * 25.5 + 1 * 50.0
        assert len(order.items) == 2

def test_cancel_order(client):
    """Тест отмены заказа"""
    # Сначала авторизуемся
    login(client, 'test@example.com', 'password123')
    
    # Получаем ID тестового заказа
    with app.app_context():
        order = Order.query.filter_by(client_name='Test Client').first()
        order_id = order.id
    
    # Отменяем заказ
    response = client.post(f'/orders/{order_id}/cancel', follow_redirects=True)
    assert response.status_code == 200
    
    # Проверяем, что заказ действительно отменен
    with app.app_context():
        order = Order.query.get(order_id)
        assert order.status == OrderStatus.CANCELLED

def test_complete_order(client):
    """Тест завершения заказа"""
    # Сначала авторизуемся
    login(client, 'test@example.com', 'password123')
    
    # Получаем ID тестового заказа
    with app.app_context():
        order = Order.query.filter_by(client_name='Test Client').first()
        order_id = order.id
    
    # Завершаем заказ
    response = client.post(f'/orders/{order_id}/complete', follow_redirects=True)
    assert response.status_code == 200
    
    # Проверяем, что заказ действительно завершен
    with app.app_context():
        order = Order.query.get(order_id)
        assert order.status == OrderStatus.COMPLETED

if __name__ == '__main__':
    pytest.main(['-v']) 