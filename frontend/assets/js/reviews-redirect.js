// Функция для проверки прав и перенаправления
async function checkUserAndRedirect(event) {
    event.preventDefault(); // Предотвращаем стандартное поведение ссылки

    try {
        const response = await fetch('http://localhost:7777/me/info', {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Accept': 'application/json'
            }
        });

        if (!response.ok) {
            // Если ошибка 401 (не авторизован) или другая, перенаправляем на обычные отзывы
            window.location.href = '/pages/exams/responses/ege-response.html';
            return;
        }

        const userData = await response.json();
        
        if (userData.is_super_user) {
            // Если пользователь админ, перенаправляем на страницу sup-ege-response.html
            window.location.href = '/pages/exams/responses/sup-responses.html';
        } else {
            // Если обычный пользователь, перенаправляем на обычные отзывы
            window.location.href = '/pages/exams/responses/ege-response.html';
        }
    } catch (error) {
        console.error('Ошибка при проверке прав:', error);
        // В случае ошибки показываем уведомление
        alert('Произошла ошибка при проверке прав доступа. Попробуйте позже.');
        // И перенаправляем на обычные отзывы
        window.location.href = '/pages/exams/responses/ege-response.html';
    }
} 