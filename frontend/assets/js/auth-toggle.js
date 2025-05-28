// Функция для проверки авторизации пользователя
async function checkAuth() {
    try {
        const response = await fetch('http://localhost:7777/me/info', {
            credentials: 'include'
        });
        if (!response.ok) return { isAuthenticated: false };
        const userData = await response.json();
        return { 
            isAuthenticated: true, 
            isSuperuser: userData.is_superuser 
        };
    } catch (error) {
        console.error('Ошибка при проверке авторизации:', error);
        return { isAuthenticated: false };
    }
}

// Функция для обновления ссылки авторизации
async function updateAuthLink() {
    const authLink = document.getElementById('auth-link');
    if (!authLink) return;

    const { isAuthenticated, isSuperuser } = await checkAuth();
    
    if (isAuthenticated) {
        authLink.textContent = 'личный кабинет';
        authLink.href = isSuperuser ? '/pages/profile/supuser.html' : '/pages/profile/standart.html';
    } else {
        authLink.textContent = 'авторизация';
        authLink.href = '/pages/auth/login.html';
    }
}

// Обновляем ссылку при загрузке страницы
document.addEventListener('DOMContentLoaded', updateAuthLink); 