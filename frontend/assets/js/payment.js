// Добавляем недостающую функцию clearPlaceholder
function clearPlaceholder(input) {
    input.placeholder = '';
}

async function handlePayment(product_slug) {
    // Находим кнопку по product_slug
    const paymentButton = document.querySelector(`.payment-button[data-product-slug="${product_slug}"]`);
    if (!paymentButton) {
        console.error('Кнопка оплаты не найдена для продукта:', product_slug);
        return;
    }

    // Извлекаем id для input и ошибки из data-атрибутов кнопки
    const inputId = paymentButton.getAttribute('data-input-id');
    const errorId = paymentButton.getAttribute('data-error-id');

    const emailInput = document.getElementById(inputId);
    const emailError = document.getElementById(errorId);
    const serverError = document.getElementById(`serverError-${product_slug}`);
    const serverErrorMessage = serverError.querySelector('.server-error-message');

    if (!emailInput || !emailError) {
        console.error('Не найдены элементы input или error для продукта:', product_slug);
        return;
    }

    // Скрываем предыдущие ошибки
    emailError.style.display = 'none';
    serverError.style.display = 'none';
    emailInput.classList.remove('error');

    const email = emailInput.value.trim();
    
    // Валидация email
    if (!email) {
        emailError.textContent = 'Введите email';
        emailError.style.display = 'block';
        emailInput.classList.add('error');
        return;
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        emailError.textContent = 'Неверный формат email';
        emailError.style.display = 'block';
        emailInput.classList.add('error');
        return;
    }

    // Индикация загрузки
    paymentButton.disabled = true;
    paymentButton.textContent = 'Отправка...';

    try {
        const response = await fetch('http://localhost:7777/payments', {
            credentials: 'include',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                product_slug: product_slug,
                email: email
            })
        });

        const data = await response.json();

        if (!response.ok) {
            // Обработка различных статус-кодов ошибок
            switch (response.status) {
                case 401:
                    throw new Error(data.detail || 'Необходима авторизация');
                case 404:
                    throw new Error(data.detail || 'Продукт не найден');
                case 409:
                    throw new Error(data.detail || 'Конфликт при создании платежа');
                default:
                    throw new Error(data.detail || `Ошибка сервера: ${response.status}`);
            }
        }

        if (!data?.payment_url) {
            throw new Error('Не удалось получить ссылку для оплаты');
        }

        // Открытие платежной страницы
        window.location.href = data.payment_url;

    } catch (error) {
        console.error('Ошибка платежа:', error);
        // Отображаем ошибку в специальном блоке
        serverErrorMessage.textContent = error.message;
        serverError.style.display = 'block';
    } finally {
        paymentButton.disabled = false;
        paymentButton.textContent = 'Страница оплаты';
    }
}

// Инициализация обработчиков событий
document.addEventListener('DOMContentLoaded', function () {
    // Обрабатываем все кнопки
    const paymentButtons = document.querySelectorAll('.payment-button');

    paymentButtons.forEach(button => {
        const productSlug = button.dataset.productSlug;
        button.addEventListener('click', () => handlePayment(productSlug));
    });
});