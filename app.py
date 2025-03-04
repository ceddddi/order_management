from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
# from flask_caching import Cache  # Временно отключаем кэширование
from werkzeug.security import generate_password_hash, check_password_hash
# from flask_swagger_ui import get_swaggerui_blueprint  # Временно отключаем Swagger UI
import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Создаем экземпляр приложения Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///new_order_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Импортируем модели и базу данных после создания приложения
# Сначала импортируем модели, затем database
from models import User, Order, OrderItem, OrderStatus, CancelledItem, db
from database import db_session, init_db

# Временно отключаем настройку кэширования
# cache_config = {
#     "DEBUG": True,
#     "CACHE_TYPE": "SimpleCache",
#     "CACHE_DEFAULT_TIMEOUT": 300  # 5 минут
# }
# app.config.from_mapping(cache_config)
# cache = Cache(app)

# Инициализация расширений
init_db(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Настройка Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'your-email@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'your-password')
mail = Mail(app)

# Временно отключаем настройку Swagger UI
# SWAGGER_URL = '/api/docs'
# API_URL = '/static/swagger.json'
# swaggerui_blueprint = get_swaggerui_blueprint(
#     SWAGGER_URL,
#     API_URL,
#     config={
#         'app_name': "Order Management API"
#     }
# )
# app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Добавляем фильтр для форматирования даты
@app.template_filter('datetime')
def format_datetime(value: datetime) -> str:
    if value is None:
        return ""
    return value.strftime('%d.%m.%Y %H:%M')

# Добавляем фильтр для форматирования денежных значений
@app.template_filter('currency')
def format_currency(value: float) -> str:
    if value is None:
        return "0,00 ₽"
    return "{:,.2f} ₽".format(value).replace(",", " ").replace(".", ",")

@login_manager.user_loader
def load_user(user_id: str) -> Optional[User]:
    return User.query.get(int(user_id))

# Создание таблиц при первом запуске
with app.app_context():
    try:
        db.create_all()
        logger.info("База данных успешно инициализирована")
    except Exception as e:
        logger.error(f"Ошибка при инициализации базы данных: {e}")

@app.before_request
def before_request():
    if current_user.is_authenticated:
        try:
            # Получаем свежие данные пользователя из базы данных
            db.session.expire_all()  # Сбрасываем все кэшированные данные
            db.session.add(current_user)  # Добавляем текущего пользователя в сессию
        except Exception as e:
            logger.error(f"Ошибка в before_request: {e}")
            db.session.rollback()

@app.route('/')
def index():
    if current_user.is_authenticated:
        # Временно отключаем кэширование
        # cache_key = f'user_stats_{current_user.id}'
        # stats = cache.get(cache_key)
        
        # if stats is None:
        active_orders = Order.query.filter_by(user_id=current_user.id, status=OrderStatus.ACTIVE).count()
        completed_orders = Order.query.filter_by(user_id=current_user.id, status=OrderStatus.COMPLETED).count()
        cancelled_orders = Order.query.filter_by(user_id=current_user.id, status=OrderStatus.CANCELLED).count()
        
        stats = {
            'active_orders': active_orders,
            'completed_orders': completed_orders,
            'cancelled_orders': cancelled_orders
        }
        
        # Сохраняем в кэш
        # cache.set(cache_key, stats)
        
        return render_template('index.html', 
                              active_orders=stats['active_orders'], 
                              completed_orders=stats['completed_orders'], 
                              cancelled_orders=stats['cancelled_orders'])
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=remember)
            flash('Вы успешно вошли в систему!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        flash('Неверный email или пароль', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Пароли не совпадают', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email уже зарегистрирован', 'danger')
            return render_template('register.html')
        
        user = User(
            name=name,
            email=email,
            password=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Регистрация успешна! Теперь вы можете войти', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('index'))

@app.route('/orders')
@login_required
# @cache.cached(timeout=60, key_prefix=lambda: f'orders_view_{current_user.id}_{request.args.get("page", 1)}_{request.args.get("status", "")}')
def orders():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = Order.query.filter_by(user_id=current_user.id)
    
    if status_filter:
        try:
            status = OrderStatus(status_filter)
            query = query.filter_by(status=status)
        except ValueError:
            pass
    
    pagination = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=10)
    
    return render_template('orders.html', 
                         orders=pagination.items,
                         pagination=pagination,
                         page=page,
                         pages=pagination.pages,
                         has_next=pagination.has_next,
                         has_prev=pagination.has_prev,
                         total=pagination.total)

def clear_user_cache(user_id: int) -> None:
    """
    Очищает кэш для конкретного пользователя.
    
    Args:
        user_id: ID пользователя
    """
    # Временно отключаем кэширование
    # cache.delete(f'user_stats_{user_id}')
    # Очистка кэша для страниц заказов сложнее, так как ключи динамические
    # Поэтому используем принудительную очистку всего кэша
    # cache.clear()
    logger.debug(f"Кэш для пользователя {user_id} очищен")

@app.route('/orders/create', methods=['GET', 'POST'])
@login_required
def create_order():
    if request.method == 'POST':
        try:
            client_name = request.form.get('client_name')
            items_data = []
            i = 0
            while True:
                product_name = request.form.get(f'product_name_{i}')
                if not product_name:
                    break
                
                quantity = int(request.form.get(f'quantity_{i}', 0))
                price = float(request.form.get(f'price_{i}', 0))
                
                if product_name and quantity > 0 and price > 0:
                    items_data.append({
                        'product_name': product_name,
                        'quantity': quantity,
                        'price': price
                    })
                i += 1
            
            if not client_name or not items_data:
                flash('Пожалуйста, заполните все обязательные поля', 'danger')
                return render_template('create_order.html')
            
            total_amount = sum(item['quantity'] * item['price'] for item in items_data)
            
            # Получаем email пользователя до входа в контекстный менеджер
            user_email = db.session.query(User.email).filter_by(id=current_user.id).scalar()
            
            # Используем контекстный менеджер для работы с БД
            with db_session() as session:
                # Получаем пользователя и увеличиваем счетчик
                user = session.query(User).with_for_update().get(current_user.id)
                user.order_counter += 1
                user_order_id = user.order_counter
                
                order = Order(
                    user_id=user.id,
                    user_order_id=user_order_id,
                    client_name=client_name,
                    total_amount=total_amount
                )
                
                session.add(order)
                session.flush()
                
                for item_data in items_data:
                    order_item = OrderItem(
                        order_id=order.id,
                        product_name=item_data['product_name'],
                        quantity=item_data['quantity'],
                        price=item_data['price']
                    )
                    session.add(order_item)
            
            logger.info(f"Заказ #{user_order_id} успешно создан пользователем {user_email}")
            flash(f'Заказ #{user_order_id} успешно создан', 'success')
            return redirect(url_for('orders'))
            
        except Exception as e:
            logger.error(f"Ошибка при создании заказа: {str(e)}")
            flash(f'Ошибка при создании заказа: {str(e)}', 'danger')
            return render_template('create_order.html')
    
    return render_template('create_order.html')

@app.route('/orders/<int:order_id>')
@login_required
def view_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('У вас нет доступа к этому заказу', 'danger')
        return redirect(url_for('orders'))
    return render_template('view_order.html', order=order)

@app.route('/orders/<int:order_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('У вас нет доступа к этому заказу', 'danger')
        return redirect(url_for('orders'))
    
    if order.status != OrderStatus.ACTIVE:
        flash('Можно редактировать только активные заказы', 'danger')
        return redirect(url_for('view_order', order_id=order_id))
    
    if request.method == 'POST':
        order.client_name = request.form.get('client_name')
        
        # Удаляем существующие товары
        for item in order.items:
            db.session.delete(item)
        
        # Добавляем новые товары
        items = []
        total_amount = 0
        i = 0
        while f'product_name_{i}' in request.form:
            product_name = request.form.get(f'product_name_{i}')
            quantity = int(request.form.get(f'quantity_{i}'))
            price = float(request.form.get(f'price_{i}'))
            
            if product_name and quantity > 0 and price > 0:
                items.append(OrderItem(
                    product_name=product_name,
                    quantity=quantity,
                    price=price
                ))
                total_amount += quantity * price
            i += 1
        
        if not items:
            flash('Добавьте хотя бы один товар', 'danger')
            return render_template('edit_order.html', order=order)
        
        order.items = items
        order.total_amount = total_amount
        db.session.commit()
        
        flash('Заказ успешно обновлен', 'success')
        return redirect(url_for('view_order', order_id=order_id))
    
    return render_template('edit_order.html', order=order)

@app.route('/orders/<int:order_id>/complete', methods=['POST'])
@login_required
def complete_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        return jsonify({'message': 'У вас нет доступа к этому заказу'}), 403
    
    if order.status != OrderStatus.ACTIVE:
        return jsonify({'message': 'Можно завершить только активный заказ'}), 400
    
    order.status = OrderStatus.COMPLETED
    db.session.commit()
    
    # Отправляем уведомление по email
    try:
        msg = Message('Заказ завершен',
                     sender=app.config['MAIL_USERNAME'],
                     recipients=[current_user.email])
        msg.body = f'''Заказ #{order.id} был успешно завершен.
        Клиент: {order.client_name}
        Сумма: {order.total_amount} ₽
        '''
        mail.send(msg)
    except Exception as e:
        app.logger.error(f'Ошибка отправки email: {e}')
    
    return jsonify({'message': 'Заказ успешно завершен'})

@app.route('/orders/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel_order(order_id: int) -> Tuple[jsonify, int]:
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    
    if order.status != OrderStatus.ACTIVE:
        return jsonify({'error': 'Только активные заказы могут быть отменены'}), 400
    
    try:
        with db_session() as session:
            # Сохраняем товары из отмененного заказа в список отмененных товаров
            for item in order.items:
                cancelled_item = CancelledItem(
                    user_id=current_user.id,
                    product_name=item.product_name,
                    quantity=item.quantity,
                    price=item.price,
                    order_reference=f'Заказ #{order.user_order_id}'
                )
                session.add(cancelled_item)
            
            order.status = OrderStatus.CANCELLED
        
        # Очищаем кэш пользователя после отмены заказа
        # clear_user_cache(current_user.id)
        
        logger.info(f"Заказ #{order.user_order_id} отменен пользователем {current_user.email}")
        return jsonify({'success': True}), 200
    except Exception as e:
        logger.error(f"Ошибка при отмене заказа #{order.user_order_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/orders/cleanup', methods=['POST'])
@login_required
def cleanup_cancelled_orders():
    try:
        # Получаем все отмененные заказы пользователя
        cancelled_orders = Order.query.filter_by(
            user_id=current_user.id,
            status=OrderStatus.CANCELLED
        ).all()
        
        # Удаляем все отмененные заказы
        for order in cancelled_orders:
            db.session.delete(order)
        
        db.session.commit()
        flash('Все отмененные заказы успешно удалены', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Произошла ошибка при удалении заказов: {str(e)}', 'danger')
    
    return redirect(url_for('orders'))

@app.route('/orders/batch/complete', methods=['POST'])
@login_required
def batch_complete_orders():
    try:
        order_ids = request.json.get('order_ids', [])
        if not order_ids:
            return jsonify({'message': 'Не выбрано ни одного заказа'}), 400
        
        # Получаем все активные заказы пользователя из выбранных
        orders = Order.query.filter(
            Order.id.in_(order_ids),
            Order.user_id == current_user.id,
            Order.status == OrderStatus.ACTIVE
        ).all()
        
        if not orders:
            return jsonify({'message': 'Нет доступных заказов для завершения'}), 400
        
        # Завершаем все выбранные заказы
        completed_count = 0
        for order in orders:
            order.status = OrderStatus.COMPLETED
            completed_count += 1
        
        db.session.commit()
        
        return jsonify({
            'message': f'Успешно завершено заказов: {completed_count}',
            'count': completed_count
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Произошла ошибка: {str(e)}'}), 500

@app.route('/orders/batch/cancel', methods=['POST'])
@login_required
def batch_cancel_orders():
    data = request.json
    order_ids = data.get('order_ids', [])
    
    if not order_ids:
        return jsonify({'message': 'Не выбрано ни одного заказа', 'count': 0}), 200
    
    orders = Order.query.filter(
        Order.id.in_(order_ids),
        Order.user_id == current_user.id,
        Order.status == OrderStatus.ACTIVE
    ).all()
    
    count = 0
    try:
        for order in orders:
            # Сохраняем товары из отмененного заказа в список отмененных товаров
            for item in order.items:
                cancelled_item = CancelledItem(
                    user_id=current_user.id,
                    product_name=item.product_name,
                    quantity=item.quantity,
                    price=item.price,
                    order_reference=f'Заказ #{order.user_order_id}'
                )
                db.session.add(cancelled_item)
            
            order.status = OrderStatus.CANCELLED
            count += 1
        
        db.session.commit()
        return jsonify({
            'message': f'Успешно отменено заказов: {count}',
            'count': count
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/profile')
@login_required
def profile():
    # Получаем все заказы пользователя
    orders = Order.query.filter_by(user_id=current_user.id).all()
    # Фильтруем заказы по статусу
    active_orders = [o for o in orders if o.status == OrderStatus.ACTIVE]
    completed_orders = [o for o in orders if o.status == OrderStatus.COMPLETED]
    
    return render_template('profile.html', 
                         orders=orders,
                         active_orders=active_orders,
                         completed_orders=completed_orders)

@app.route('/toggle_theme', methods=['POST'])
def toggle_theme():
    # Переключаем тему
    session['dark_mode'] = not session.get('dark_mode', False)
    return jsonify({'success': True})

@app.route('/cancelled-items')
@login_required
def cancelled_items():
    page = request.args.get('page', 1, type=int)
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    query = CancelledItem.query.filter_by(user_id=current_user.id)
    
    if date_from:
        query = query.filter(CancelledItem.cancelled_at >= date_from)
    if date_to:
        query = query.filter(CancelledItem.cancelled_at <= date_to)
    
    pagination = query.order_by(CancelledItem.cancelled_at.desc()).paginate(page=page, per_page=10)
    items = pagination.items
    
    return render_template('cancelled_items.html', 
                         items=items,
                         pages=pagination.pages,
                         page=pagination.page,
                         has_next=pagination.has_next,
                         has_prev=pagination.has_prev,
                         total=pagination.total)

if __name__ == '__main__':
    app.run(debug=True) 