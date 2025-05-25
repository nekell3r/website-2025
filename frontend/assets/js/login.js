document.addEventListener('DOMContentLoaded', function() {
    // Инициализация маски для телефона
    const phoneInput = document.getElementById('phone');
    $(phoneInput).inputmask("+7 (999) 999-99-99");

    // Обработка показа/скрытия пароля
    const togglePassword = document.querySelector('.toggle-password');
    const passwordInput = document.getElementById('password');

    togglePassword.addEventListener('click', function() {
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
        this.querySelector('.eye-icon').style.opacity = type === 'password' ? '1' : '0.5';
    });

    // Обработка отправки формы
    document.getElementById('submit-login').addEventListener('click', async function() {
        const errorBlock = document.getElementById('login-error');
        errorBlock.textContent = '';

        // Получаем значения полей
        const rawPhone = phoneInput.value.trim();
        const cleanedPhone = rawPhone.replace(/\D/g, '');
        const password = passwordInput.value;

        // Валидация
        if (!cleanedPhone || cleanedPhone.length !== 11 || !/^7\d{10}$/.test(cleanedPhone)) {
            errorBlock.textContent = 'Введите корректный номер телефона';
            return;
        }

        if (!password) {
            errorBlock.textContent = 'Введите пароль';
            return;
        }

        try {
            const response = await fetch('http://localhost:7777/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    phone: '+' + cleanedPhone,
                    password: password
                }),
                credentials: 'include'
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData?.detail || `Ошибка: ${response.status}`);
            }

            // Если ответ успешный, сразу перенаправляем на dashboard
            window.location.href = '../profile/dashboard.html';
            
        } catch (error) {
            errorBlock.textContent = error.message || 'Ошибка при входе';
        }
    });
}); 