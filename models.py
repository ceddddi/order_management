from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import enum
from typing import List, Optional, Dict, Any

db = SQLAlchemy()

class OrderStatus(enum.Enum):
    ACTIVE = 'active'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    orders = db.relationship('Order', backref='user', lazy=True)
    cancelled_items = db.relationship('CancelledItem', backref='user', lazy=True)
    # Счетчик для пользовательских ID заказов
    order_counter = db.Column(db.Integer, default=0)

    def __repr__(self) -> str:
        return f'<User {self.email}>'

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Пользовательский ID заказа (начинается с 1 для каждого пользователя)
    user_order_id = db.Column(db.Integer, nullable=False)
    client_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.Enum(OrderStatus), default=OrderStatus.ACTIVE)
    total_amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

    @property
    def status_display(self) -> str:
        return {
            OrderStatus.ACTIVE: 'Активный',
            OrderStatus.COMPLETED: 'Завершен',
            OrderStatus.CANCELLED: 'Отменен'
        }.get(self.status, '')

    @property
    def status_color(self) -> str:
        return {
            OrderStatus.ACTIVE: 'primary',
            OrderStatus.COMPLETED: 'success',
            OrderStatus.CANCELLED: 'danger'
        }.get(self.status, '')

    def __repr__(self) -> str:
        return f'<Order {self.user_order_id}>'

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def subtotal(self) -> float:
        return self.quantity * self.price

    def __repr__(self) -> str:
        return f'<OrderItem {self.product_name}>'

class CancelledItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    order_reference = db.Column(db.String(50), nullable=False)  # Ссылка на номер заказа, из которого был отменен товар
    cancelled_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def subtotal(self) -> float:
        return self.quantity * self.price

    def __repr__(self) -> str:
        return f'<CancelledItem {self.product_name}>' 