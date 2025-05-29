// Скрипт проверки аутентификации
fetch('http://localhost:7777/me/info', { // Используем относительный путь, если бэкенд на том же домене
    credentials: 'include', // Важно для отправки cookies
    headers: {
        'Content-Type': 'application/json',
        // 'X-CSRFToken': getCookie('csrftoken') // Раскомментируйте и реализуйте getCookie, если используете CSRF-токены
    }
})
.then(response => {
    if (response.status === 401) {
        // Пользователь не авторизован, перенаправляем на страницу входа
        // Путь к login.html должен быть относительным из директории, где находится HTML-файл, использующий этот скрипт
        // Для standart.html и supuser.html, находящихся в /pages/profile/, путь будет ../auth/login.html
        if (window.location.pathname.includes('profile/')) {
            window.location.href = '../auth/login.html';
        } else {
            // Фолбэк для других возможных расположений или прямой вызов из корня frontend
            window.location.href = 'pages/auth/login.html';
        }
        return Promise.reject('User not authenticated'); // Останавливаем дальнейшую обработку
    }
    if (!response.ok) {
        // Обработка других ошибок HTTP, если необходимо
        console.error('Ошибка ответа сервера:', response.status);
        return Promise.reject('Server error: ' + response.status); // Останавливаем дальнейшую обработку
    }
    return response.json(); // Парсим JSON, если ответ успешный
})
.then(data => {
    // Проверяем, находимся ли мы на странице supuser.html
    if (window.location.pathname.includes('supuser.html')) {
        if (!data.is_super_user) {
            // Если пользователь не суперюзер, перенаправляем на главную страницу
            // Путь к index.html должен быть относительным
            window.location.href = '/pages/error/403.html';
        }
        // Если is_super_user === true, ничего не делаем, страница supuser.html загружается
    }
    // Для других страниц (например, standart.html) после успешной аутентификации и получения данных
    // ничего дополнительно делать не нужно, страница просто загружается.
})
.catch(error => {
    if (error !== 'User not authenticated' && !error.startsWith('Server error:')) {
        console.error('Ошибка при проверке аутентификации или прав:', error);
    }
    // Если ошибка 'User not authenticated' или 'Server error', она уже обработана (перенаправление или логирование)
    // Можно добавить специфическую обработку для страницы, если она не загрузилась,
    // например, показать сообщение об ошибке, но текущая логика просто не даст странице загрузиться.
});

// Вспомогательная функция для получения CSRF-токена, если необходимо
// function getCookie(name) {
//     let cookieValue = null;
//     if (document.cookie && document.cookie !== '') {
//         const cookies = document.cookie.split(';');
//         for (let i = 0; i < cookies.length; i++) {
//             const cookie = cookies[i].trim();
//             if (cookie.substring(0, name.length + 1) === (name + '=')) {
//                 cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
//                 break;
//             }
//         }
//     }
//     return cookieValue;
// } 