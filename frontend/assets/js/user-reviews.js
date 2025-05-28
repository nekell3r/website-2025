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
    // Если у card есть background-color, то padding будет виден.
    // Убедимся, что нет лишнего padding-bottom у самой card.
    // card.style.padding = '15px 15px 0 15px'; // Пример, если общий padding был 15px

    // Создаем заголовок карточки
    const cardHeader = document.createElement('div');
    cardHeader.className = 'card-header';
    // Предполагаем, что стили для cardHeader (включая padding) заданы в CSS или ранее и они корректны

    const cardHeaderContent = document.createElement('div');
    cardHeaderContent.className = 'card-header-content-wrapper';
    cardHeaderContent.style.cssText = 'display: flex; width: 100%; justify-content: space-between; align-items: flex-start;';

    const info = document.createElement('div');
    info.className = 'info';
    
    const examInfo = document.createElement('div');
    examInfo.className = 'exam';
    examInfo.innerHTML = `${review.exam}: <strong>${review.result}</strong>`;

    const dateInfo = document.createElement('div');
    dateInfo.className = 'date';
    dateInfo.innerHTML = `Дата публикации: <strong>${formatDate(review.created_at)}</strong>`;

    info.appendChild(examInfo);
    info.appendChild(dateInfo);

    const avatar = document.createElement('img');
    avatar.src = '../../assets/img/avatar.jpg'; 
    avatar.alt = 'Аватар';
    // Предполагаем, что стили для avatar (размеры, border-radius) заданы в CSS или ранее

    cardHeaderContent.appendChild(info);
    cardHeaderContent.appendChild(avatar);
    cardHeader.appendChild(cardHeaderContent);

    // Тело карточки
    const cardBody = document.createElement('div');
    cardBody.className = 'card-body';
    // Явно устанавливаем padding для cardBody, с минимальным или нулевым padding-bottom
    // Пример: 15px сверху, 15px по бокам, 5px снизу.
    // Если нужен другой верхний/боковой padding, его нужно указать здесь.
    // Если cardBody не должен иметь боковых/верхних отступов от card, то можно поставить padding: 0 0 5px 0;
    cardBody.style.padding = '15px 15px 5px 15px'; // (top, right, bottom, left)

    const reviewContainer = document.createElement('div');
    reviewContainer.className = 'review-container';
    reviewContainer.style.marginBottom = '0';

    const reviewText = document.createElement('div');
    reviewText.className = 'review-text';
    reviewText.textContent = review.review;
    reviewText.style.maxHeight = '100px';
    reviewText.style.overflow = 'hidden';
    reviewText.style.marginBottom = '5px';

    reviewContainer.appendChild(reviewText);

    const buttonsContainer = document.createElement('div');
    buttonsContainer.style.cssText = 'display: flex; justify-content: space-between; align-items: flex-start; width: 100%; margin-top: 0; margin-bottom: 0;';

    const leftButtonsSubContainer = document.createElement('div');
    const rightButtonsSubContainer = document.createElement('div');
    rightButtonsSubContainer.style.cssText = 'display: flex; flex-direction: column; align-items: flex-end; gap: 0px;';

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
    deleteButton.style.cssText = 'color: #E0407B; font-size: 0.9em; background: transparent; border: none; padding: 0; cursor: pointer; margin-bottom: 5px;';
    deleteButton.onclick = () => deleteReview(review.id);
    
    const editButton = document.createElement('button');
    editButton.className = 'edit-review';
    editButton.textContent = 'Редактировать';
    editButton.style.cssText = 'color: #E0407B; font-size: 0.9em; background: transparent; border: none; padding: 0; cursor: pointer;';
    editButton.onclick = (e) => {
        e.preventDefault(); 
        editReview(review.id);
    };

    rightButtonsSubContainer.appendChild(deleteButton);
    rightButtonsSubContainer.appendChild(editButton);

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