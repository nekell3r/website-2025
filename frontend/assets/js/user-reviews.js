// Функция для форматирования даты
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU');
}

// Функция для удаления отзыва
async function deleteReview(reviewId) {
    if (confirm('Вы уверены, что хотите удалить этот отзыв?')) {
        try {
            const response = await fetch(`http://localhost:7777/reviews/${reviewId}`, {
                credentials: 'include',
                method: 'DELETE'
            });

            if (response.ok) {
                const card = document.querySelector(`[data-review-id="${reviewId}"]`);
                if (card) {
                    card.remove();
                }
            } else {
                throw new Error('Ошибка при удалении отзыва');
            }
        } catch (error) {
            console.error('Ошибка:', error);
            alert('Не удалось удалить отзыв. Пожалуйста, попробуйте позже.');
        }
    }
}

// Функция для редактирования отзыва
function editReview(reviewId) {
    window.location.href = `../materials/red.html?reviewId=${reviewId}`;
}

// Функция для создания карточки отзыва
function createReviewCard(review) {
    const card = document.createElement('div');
    card.className = 'card';
    card.setAttribute('data-review-id', review.id);
    card.style.minWidth = '300px';

    // Создаем заголовок карточки
    const cardHeader = document.createElement('div');
    cardHeader.className = 'card-header';

    const cardHeaderContent = document.createElement('div');
    cardHeaderContent.className = 'card-header-content-wrapper';
    cardHeaderContent.style.cssText = 'display: flex; width: 100%; justify-content: space-between; align-items: flex-start;';

    // Информация о пользователе (левая часть заголовка)
    const info = document.createElement('div');
    info.className = 'info';
    // Добавляем flex-контейнер для info, чтобы элементы внутри располагались вертикально
    info.style.cssText = 'display: flex; flex-direction: column; align-items: flex-start;';
    
    const editButton = document.createElement('a');
    editButton.href = '#';
    editButton.className = 'edit-review-link';
    editButton.textContent = 'Редактировать';
    editButton.style.cssText = 'display: inline-block; font-size: 10px; color: #fff; text-decoration: none; border: 1px solid #fff; padding: 2px 5px; border-radius: 10px; margin-bottom: 5px;';
    editButton.onclick = (e) => {
        e.preventDefault();
        editReview(review.id);
    };

    const examInfo = document.createElement('div');
    examInfo.className = 'exam';
    examInfo.innerHTML = `${review.exam}: <strong>${review.result}</strong>`;

    const dateInfo = document.createElement('div');
    dateInfo.className = 'date';
    dateInfo.innerHTML = `Дата публикации: <strong>${formatDate(review.created_at)}</strong>`;

    info.appendChild(editButton); 
    info.appendChild(examInfo);
    info.appendChild(dateInfo);

    // Аватар (правая часть заголовка)
    const avatar = document.createElement('img');
    avatar.src = '../../assets/img/avatar.jpg'; 
    avatar.alt = 'Аватар';

    cardHeaderContent.appendChild(info);
    cardHeaderContent.appendChild(avatar);
    cardHeader.appendChild(cardHeaderContent);

    // Тело карточки
    const cardBody = document.createElement('div');
    cardBody.className = 'card-body';

    const reviewContainer = document.createElement('div');
    reviewContainer.className = 'review-container';

    const reviewText = document.createElement('div');
    reviewText.className = 'review-text';
    reviewText.textContent = review.review;
    reviewText.style.maxHeight = '100px';
    reviewText.style.overflow = 'hidden';

    reviewContainer.appendChild(reviewText);

    // Добавляем кнопки под текстом отзыва
    const buttonsContainer = document.createElement('div');
    buttonsContainer.style.cssText = 'display: flex; justify-content: space-between; align-items: center; width: 100%; margin-top: 10px;';

    const leftButtonsSubContainer = document.createElement('div');
    const rightButtonsSubContainer = document.createElement('div');

    if (review.review.length > 100) { 
        const readMoreBtn = document.createElement('button');
        readMoreBtn.className = 'read-more'; 
        readMoreBtn.textContent = 'Читать полностью';
        readMoreBtn.style.cssText = 'color: #E0407B; font-size: 0.9em; background: transparent; border: none; padding: 0; cursor: pointer;';
        readMoreBtn.onclick = function() {
            if (reviewText.style.maxHeight !== 'none') {
                reviewText.style.maxHeight = 'none';
                this.textContent = 'Свернуть';
            } else {
                reviewText.style.maxHeight = '100px';
                this.textContent = 'Читать полностью';
            }
        };
        leftButtonsSubContainer.appendChild(readMoreBtn);
    }

    const deleteButton = document.createElement('button');
    deleteButton.className = 'delete-review'; 
    deleteButton.textContent = 'Удалить';
    deleteButton.style.cssText = 'color: #E0407B; font-size: 0.9em; background: transparent; border: none; padding: 0; cursor: pointer;';
    deleteButton.onclick = () => deleteReview(review.id);
    rightButtonsSubContainer.appendChild(deleteButton);

    buttonsContainer.appendChild(leftButtonsSubContainer);
    buttonsContainer.appendChild(rightButtonsSubContainer);

    reviewContainer.appendChild(buttonsContainer);
    cardBody.appendChild(reviewContainer);

    card.appendChild(cardHeader);
    card.appendChild(cardBody);

    return card;
}

// Функция для загрузки отзывов
async function loadUserReviews() {
    try {
        const response = await fetch('http://localhost:7777/me/reviews', {
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            if (response.status === 401) {
                alert('Сессия истекла или вы не авторизованы. Пожалуйста, войдите снова.');
                // window.location.href = '/auth/login.html'; // Consider redirecting
                return;
            }
            throw new Error(`Ошибка при загрузке отзывов: ${response.statusText}`);
        }

        const reviews = await response.json();
        console.log('Received reviews:', reviews);

        const container = document.getElementById('container');
        if (!container) {
            console.error('Container element not found');
            alert('Ошибка: Контейнер для отзывов не найден на странице.');
            return;
        }
        container.innerHTML = ''; 

        if (reviews.length === 0) {
            container.innerHTML = '<p style="color: #ccc; text-align: center;">У вас пока нет отзывов.</p>';
        } else {
            reviews.forEach(review => {
                const card = createReviewCard(review);
                container.appendChild(card);
            });
        }

        const sentinel = document.getElementById('sentinel');
        if (sentinel) {
            sentinel.style.display = 'none';
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert(`Не удалось загрузить отзывы. Пожалуйста, попробуйте позже. (${error.message})`);
        const container = document.getElementById('container');
        if (container) {
            container.innerHTML = '<p style="color: red; text-align: center;">Не удалось загрузить отзывы. Пожалуйста, обновите страницу или попробуйте позже.</p>';
        }
    }
}

// Загружаем отзывы при загрузке страницы
document.addEventListener('DOMContentLoaded', loadUserReviews); 