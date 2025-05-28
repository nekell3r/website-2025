// Функция для проверки авторизации пользователя
async function checkAuth() {
    try {
        const response = await fetch('http://localhost:7777/me', {
            credentials: 'include'
        });
        return response.ok;
    } catch (error) {
        console.error('Ошибка при проверке авторизации:', error);
        return false;
    }
}

// Функция для обновления ссылки авторизации
async function updateAuthLink() {
    const authLink = document.getElementById('auth-link');
    if (!authLink) return;

    const isAuthenticated = await checkAuth();
    
    if (isAuthenticated) {
        authLink.textContent = 'личный кабинет';
        authLink.href = '/pages/profile/standart.html';
    } else {
        authLink.textContent = 'авторизация';
        authLink.href = '/pages/auth/login.html';
    }
}

// Обновляем ссылку при загрузке страницы
document.addEventListener('DOMContentLoaded', updateAuthLink); 