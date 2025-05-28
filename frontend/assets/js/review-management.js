// Функция для удаления отзыва
function deleteReview(reviewId) {
    if (confirm('Вы уверены, что хотите удалить этот отзыв?')) {
        console.log('Удаление отзыва с ID:', reviewId);
        // TODO: Добавить API-запрос для удаления отзыва
        // fetch(`/api/reviews/${reviewId}`, {
        //     method: 'DELETE',
        //     headers: {
        //         'Authorization': `Bearer ${localStorage.getItem('token')}`
        //     }
        // })
        // .then(response => {
        //     if (response.ok) {
        //         // Удалить карточку отзыва из DOM
        //         document.querySelector(`[data-review-id="${reviewId}"]`).remove();
        //     }
        // });
    }
}

// Функция для редактирования отзыва
function editReview(reviewId) {
    console.log('Редактирование отзыва с ID:', reviewId);
    // Перенаправление на страницу редактирования
    window.location.href = `../materials/red.html?reviewId=${reviewId}`;
}

// Функция для добавления кнопок управления к карточке отзыва
function addManagementButtons(reviewCard, reviewId) {
    const managementDiv = document.createElement('div');
    managementDiv.className = 'review-management';
    managementDiv.style.cssText = 'position: absolute; right: 10px; bottom: 10px; display: flex; gap: 10px;';

    // Кнопка редактирования
    const editButton = document.createElement('button');
    editButton.className = 'edit-button';
    editButton.textContent = 'Редактировать';
    editButton.style.cssText = `
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 5px 10px;
        border-radius: 5px;
        cursor: pointer;
        font-size: 14px;
    `;
    editButton.onclick = () => editReview(reviewId);

    // Кнопка удаления
    const deleteButton = document.createElement('button');
    deleteButton.className = 'delete-button';
    deleteButton.textContent = 'Удалить';
    deleteButton.style.cssText = `
        background-color: #f44336;
        color: white;
        border: none;
        padding: 5px 10px;
        border-radius: 5px;
        cursor: pointer;
        font-size: 14px;
    `;
    deleteButton.onclick = () => deleteReview(reviewId);

    managementDiv.appendChild(editButton);
    managementDiv.appendChild(deleteButton);
    
    // Добавляем кнопки в карточку отзыва
    reviewCard.style.position = 'relative';
    reviewCard.appendChild(managementDiv);
}

// Экспортируем функцию для использования в main-reviews.js
window.addManagementButtons = addManagementButtons; 