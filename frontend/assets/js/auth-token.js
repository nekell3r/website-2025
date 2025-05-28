document.getElementById('auth-link').addEventListener('click', async function(e) {
    e.preventDefault();

    
        const response = await fetch('http://localhost:7777/me/info', {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            }
        });
        console.log(response);
        console.log(response.detail);
        if (response.status === 401) {
            // Пользователь не авторизован
            window.location.href = '/pages/error/401.html';
            return;
        }
        if (response.status === 404) {
            window.location.href = '/pages/auth/login.html';
            return;
        }


        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const userData = await response.json();
        console.log(userData);
        if (userData && userData.id && userData.name) {
            // Сохраняем данные пользователя перед переходом
            sessionStorage.setItem('userData', JSON.stringify(userData));

            // Перенаправляем в личный кабинет
            window.location.href = '/pages/profile/standart.html';
        } else {
            throw new Error('Получены некорректные данные пользователя');
        }
    })