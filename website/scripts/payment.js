async function handlePayment(product_slug) {
    const email = document.getElementById('userInput').value.trim();
    const emailError = document.getElementById('emailError');
    const paymentButton = document.querySelector('.payment-button');

    // Валидация email
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        emailError.textContent = !email ? 'Введите email' : 'Неверный формат email';
        emailError.style.display = 'block';
        document.getElementById('userInput').classList.add('error');
        return;
    }

    // Индикация загрузки
    paymentButton.disabled = true;
    paymentButton.textContent = 'Отправка...';

    try {
        // Добавляем timestamp для избежания кеширования
        const apiUrl = new URL('https://2589-45-12-109-171.ngrok-free.app/payments');
        apiUrl.searchParams.append('t', Date.now());

        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'ngrok-skip-browser-warning': 'true'
            },
            body: JSON.stringify({
                product_slug: product_slug,
                email: email
            }),
            credentials: 'include',
            mode: 'cors'
        });

        // Переносим объявление data до её использования
        const data = await response.json();
        console.log('Полный ответ:', data);

        if (!response.ok) {
            // Используем data, которая теперь объявлена выше
            const errorDetail = data.detail || 'Неизвестная ошибка сервера';
            
            const errorMessages = {
                'Email is required': 'Пожалуйста, введите email',
                'Invalid email format': 'Неверный формат email',
                'Payment failed': 'Ошибка при создании платежа'
            };
            
            throw new Error(errorMessages[errorDetail] || errorDetail);
        }

        if (!data?.payment_url) {
            throw new Error('Ссылка для оплаты не получена в ответе');
        }

        try {
            const paymentWindow = window.open(data.payment_url, '_blank', 'noopener,noreferrer');
            if (!paymentWindow) {
                window.location.href = data.payment_url;
            }
        } catch (windowError) {
            console.error('Ошибка открытия окна:', windowError);
            window.location.href = data.payment_url;
        }

    } catch (error) {
        console.error('Полная ошибка:', error);
        
        let errorMessage = 'Оплата не прошла';
        if (error.message.includes('Failed to fetch')) {
            errorMessage = 'Проблема с соединением. Проверьте интернет и попробуйте ещё раз.';
        } else if (error.message.includes('NetworkError')) {
            errorMessage = 'Сервер не отвечает. Попробуйте позже.';
        } else {
            errorMessage = error.message;
        }
        
        alert(errorMessage);
    } finally {
        paymentButton.disabled = false;
        paymentButton.textContent = 'Страница оплаты';
    }
}