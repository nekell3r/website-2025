document.addEventListener('DOMContentLoaded', function() {
    const phoneInput = document.getElementById('phone-input');
    const codeInput = document.getElementById('code-input');
    
    const sendCodeButton = document.getElementById('send-code-button');
    const submitRecoveryButton = document.getElementById('submit-recovery');

    const phoneErrorDiv = document.getElementById('phone-error'); // Ошибки для поля телефона
    const codeErrorDiv = document.getElementById('code-error'); // Ошибки для поля кода
    const sendCodeErrorDiv = document.getElementById('send-code-error'); // Ошибки для кнопки "Отправить код"
    const submitErrorDiv = document.getElementById('submit-error'); // Ошибки для кнопки "Восстановить пароль"

    const API_BASE_URL = 'http://localhost:7777';

    // Инициализация маски для телефона
    if (phoneInput) {
        $(phoneInput).inputmask("+7 (999) 999-99-99");
    }

    function clearErrors() {
        if (phoneErrorDiv) phoneErrorDiv.textContent = '';
        if (codeErrorDiv) codeErrorDiv.textContent = '';
        if (sendCodeErrorDiv) sendCodeErrorDiv.textContent = '';
        if (submitErrorDiv) submitErrorDiv.textContent = '';
    }

    // 1. Обработчик для кнопки "Отправить код"
    if (sendCodeButton) {
        sendCodeButton.addEventListener('click', async function() {
            clearErrors();
            const rawPhone = phoneInput ? phoneInput.value.trim() : '';
            const cleanedPhone = rawPhone.replace(/\D/g, '');

            if (!cleanedPhone || cleanedPhone.length !== 11 || !/^7\d{10}$/.test(cleanedPhone)) {
                if (sendCodeErrorDiv) sendCodeErrorDiv.textContent = 'Введите корректный номер телефона (Формат: +7 XXX XXX-XX-XX)';
                else if (phoneErrorDiv) phoneErrorDiv.textContent = 'Введите корректный номер телефона (Формат: +7 XXX XXX-XX-XX)'; // Fallback
                return;
            }

            try {
                const response = await fetch(`${API_BASE_URL}/auth/reset`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ phone: '+' + cleanedPhone }),
                    credentials: 'include' 
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({ detail: `Ошибка сервера: ${response.status}` }));
                    throw new Error(errorData.detail || `Ошибка: ${response.status}`);
                }
                
                // const responseData = await response.json(); // Если сервер возвращает какие-то данные
                if (sendCodeErrorDiv) {
                    sendCodeErrorDiv.style.color = 'green';
                    sendCodeErrorDiv.textContent = 'Код успешно отправлен на ваш номер телефона!';
                }

            } catch (error) {
                if (sendCodeErrorDiv) {
                    sendCodeErrorDiv.style.color = 'red';
                    sendCodeErrorDiv.textContent = error.message || 'Не удалось отправить код.';
                }
            }
        });
    }

    // 2. Обработчик для кнопки "Восстановить пароль" (проверка кода)
    if (submitRecoveryButton) {
        submitRecoveryButton.addEventListener('click', async function() {
            clearErrors();
            const rawPhone = phoneInput ? phoneInput.value.trim() : '';
            const cleanedPhone = rawPhone.replace(/\D/g, '');
            const codeValue = codeInput ? codeInput.value.trim() : '';

            let isValid = true;
            if (!cleanedPhone || cleanedPhone.length !== 11 || !/^7\d{10}$/.test(cleanedPhone)) {
                if (phoneErrorDiv) phoneErrorDiv.textContent = 'Введите корректный номер телефона.';
                isValid = false;
            }
            if (!codeValue) { // Простая проверка на непустое значение кода
                if (codeErrorDiv) codeErrorDiv.textContent = 'Введите код из СМС.';
                isValid = false;
            }
            if (!isValid) return;

            try {
                const response = await fetch(`${API_BASE_URL}/auth/reset/verify`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        phone: '+' + cleanedPhone,
                        code: codeValue
                    }),
                    credentials: 'include'
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({ detail: `Ошибка сервера: ${response.status}` }));
                    throw new Error(errorData.detail || `Ошибка: ${response.status}`);
                }

                // const responseData = await response.json(); // Если сервер возвращает какие-то данные
                
                // Сохраняем номер телефона в sessionStorage
                sessionStorage.setItem('phoneForPasswordReset', '+' + cleanedPhone);
                
                if (submitErrorDiv) {
                    submitErrorDiv.style.color = 'green';
                    submitErrorDiv.textContent = 'Код подтвержден! Перенаправление на страницу смены пароля...';
                }
                
                // Перенаправление на страницу смены пароля
                window.location.href = 'password-settings.html'; 

            } catch (error) {
                if (submitErrorDiv) {
                    submitErrorDiv.style.color = 'red';
                    submitErrorDiv.textContent = error.message || 'Ошибка при проверке кода.';
                }
            }
        });
    }
}); 