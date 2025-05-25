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

    if (!emailInput || !emailError) {
        console.error('Не найдены элементы input или error для продукта:', product_slug);
        return;
    }

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

    // Сброс ошибок
    emailError.style.display = 'none';
    emailInput.classList.remove('error');

    // Индикация загрузки
    paymentButton.disabled = true;
    paymentButton.textContent = 'Отправка...';

    try {
        const response = await fetch('http://localhost:7777/payments', {
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

        // Обработка ответа
        if (!response.ok) {
            const errorData = await parseResponse(response);
            throw new Error(errorData.message || `Ошибка сервера: ${response.status}`);
        }

        const data = await parseResponse(response);
        
        if (!data?.payment_url) {
            throw new Error('Не удалось получить ссылку для оплаты');
        }

        // Открытие платежной страницы
        window.location.href = data.payment_url;
    } catch (error) {
        console.error('Ошибка платежа:', error);
        showPaymentError(error);
    } finally {
        paymentButton.disabled = false;
        paymentButton.textContent = 'Страница оплаты';
    }
}

async function parseResponse(response) {
    try {
        return await response.json();
    } catch (e) {
        console.error('Ошибка парсинга ответа:', e);
        return { message: 'Ошибка обработки ответа сервера' };
    }
}

function showPaymentError(error) {
    const errorMessages = {
        'Failed to fetch': 'Нет соединения с сервером. Проверьте интернет-соединение.',
        'NetworkError': 'Проблемы с интернет-соединением',
        'AbortError': 'Превышено время ожидания ответа от сервера'
    };

    const userMessage = errorMessages[error.name] || 
                      errorMessages[error.message] || 
                      error.message || 
                      'Произошла неизвестная ошибка при обработке платежа';
    
    alert(userMessage);
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