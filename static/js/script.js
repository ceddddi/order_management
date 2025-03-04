// Функция для подтверждения действий
function confirmAction(message) {
    return confirm(message);
}

// Функция для отображения уведомлений
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.role = 'alert';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    document.querySelector('.container').insertAdjacentElement('afterbegin', notification);
    
    // Автоматически скрыть уведомление через 5 секунд
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Функция для валидации форм
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;

    let isValid = true;
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });

    return isValid;
}

// Функция для обновления статуса заказа
async function updateOrderStatus(orderId, status) {
    try {
        const response = await fetch(`/orders/${orderId}/${status}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (response.ok) {
            showNotification('Статус заказа успешно обновлен', 'success');
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            const error = await response.json();
            showNotification(error.message || 'Произошла ошибка при обновлении статуса', 'danger');
        }
    } catch (error) {
        showNotification('Произошла ошибка при обновлении статуса', 'danger');
    }
}

// Функция для форматирования даты
function formatDate(date) {
    return new Date(date).toLocaleString('ru-RU', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Функция для форматирования суммы
function formatCurrency(amount) {
    return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'RUB'
    }).format(amount);
}

// Обработчики событий при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    // Инициализация подсказок Bootstrap
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });

    // Валидация форм при отправке
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            if (!validateForm(form.id)) {
                e.preventDefault();
                showNotification('Пожалуйста, заполните все обязательные поля', 'warning');
            }
        });
    });

    // Обработка изменения фильтров
    const filterForm = document.getElementById('filterForm');
    if (filterForm) {
        const filterInputs = filterForm.querySelectorAll('select, input[type="date"]');
        filterInputs.forEach(input => {
            input.addEventListener('change', () => {
                filterForm.submit();
            });
        });
    }
}); 