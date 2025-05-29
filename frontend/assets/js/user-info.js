// Функция для форматирования телефонного номера
function formatPhoneNumber(phone) {
    if (!phone) return '';
    // Убираем 'tel:' из начала строки если есть
    phone = phone.replace('tel:', '');
    return phone;
}

let isEditing = false;
let currentUserInfo = null;

// Функция для переключения режима редактирования
function toggleEditMode() {
    const editButton = document.querySelector('.edit-button');
    const editableFields = document.querySelectorAll('.editable');
    isEditing = !isEditing;

    if (isEditing) {
        // Включаем режим редактирования
        editButton.textContent = 'Сохранить изменения';
        editableFields.forEach(field => {
            const textElement = field.querySelector('.field-value');
            const input = field.querySelector('.edit-input');
            
            if (textElement && input) {
                input.value = textElement.textContent || '';
                textElement.style.display = 'none';
                input.style.display = 'block';
            }
        });
    } else {
        // Сохраняем изменения
        const updatedData = {};
        editableFields.forEach(field => {
            const input = field.querySelector('.edit-input');
            const fieldName = field.getAttribute('data-field');
            if (input && fieldName) {
                updatedData[fieldName] = input.value;
            }
        });

        saveUserInfo(updatedData);
    }
}

// Функция для сохранения информации о пользователе
async function saveUserInfo(data) {
    try {
        const response = await fetch('http://localhost:7777/me/info', {
            method: 'PATCH',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: data.name,
                surname: data.surname
            })
        });

        if (!response.ok) {
            throw new Error('Ошибка при сохранении данных');
        }

        // Перезагружаем информацию о пользователе
        await loadUserInfo();
        
        // Возвращаем кнопку в исходное состояние
        const editButton = document.querySelector('.edit-button');
        if (editButton) {
            editButton.textContent = 'Редактировать профиль';
        }
        
        // Скрываем поля ввода и показываем текст
        const editableFields = document.querySelectorAll('.editable');
        editableFields.forEach(field => {
            const textElement = field.querySelector('.field-value');
            const input = field.querySelector('.edit-input');
            if (textElement && input) {
                textElement.style.display = 'block';
                input.style.display = 'none';
            }
        });

    } catch (error) {
        console.error('Ошибка при сохранении:', error);
        alert('Не удалось сохранить изменения. Пожалуйста, попробуйте позже.');
    }
}

// Функция для загрузки информации о пользователе
async function loadUserInfo() {
    try {
        const response = await fetch('http://localhost:7777/me/info', {
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            if (response.status === 401) {
                console.error('Пользователь не авторизован');
                return;
            }
            throw new Error(`Ошибка при загрузке информации: ${response.statusText}`);
        }

        const userInfo = await response.json();
        currentUserInfo = userInfo;
        
        // Обновляем информацию на странице
        const nameElement = document.querySelector('[data-field="name"] .field-value');
        const surnameElement = document.querySelector('[data-field="surname"] .field-value');
        const phoneElement = document.querySelector('[data-field="phone"] .field-value');
        const emailElement = document.querySelector('[data-field="email"] .field-value');

        if (nameElement) nameElement.textContent = userInfo.name || '';
        if (surnameElement) surnameElement.textContent = userInfo.surname || '';
        if (phoneElement) phoneElement.textContent = formatPhoneNumber(userInfo.phone) || '';
        if (emailElement) emailElement.textContent = userInfo.email || '';

    } catch (error) {
        console.error('Ошибка при загрузке информации о пользователе:', error);
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    loadUserInfo();
    
    // Добавляем обработчик для кнопки редактирования
    const editButton = document.querySelector('.edit-button');
    if (editButton) {
        editButton.addEventListener('click', toggleEditMode);
    }
}); 