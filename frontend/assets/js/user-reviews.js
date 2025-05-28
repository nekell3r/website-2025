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

// --- Начало кода для модального окна редактирования ---
// Объявляем переменные здесь, но не инициализируем их сразу
let editReviewModalOverlay, editReviewModalContent, editingReviewIdInput, 
    editReviewTextInput, editReviewScoreInput, cancelEditReviewButton, saveReviewChangesButton;

async function openEditModal(review) {
    // Проверка перенесена внутрь DOMContentLoaded для инициализации элементов
    if (!editReviewModalOverlay || !editReviewTextInput || !editReviewScoreInput || !editingReviewIdInput) {
        console.error('Элементы модального окна не найдены! Убедитесь, что HTML добавлен на страницу и ID корректны.');
        alert('Произошла ошибка при открытии окна редактирования. Элементы не найдены.');
        return;
    }
    editingReviewIdInput.value = review.id;
    editReviewTextInput.value = review.review;
    editReviewScoreInput.value = review.result;

    // Устанавливаем ограничения в зависимости от типа экзамена
    if (review.exam.toLowerCase().includes('огэ')) {
        editReviewScoreInput.min = 2;
        editReviewScoreInput.max = 5;
        editReviewScoreInput.placeholder = 'Оценка от 2 до 5';
    } else if (review.exam.toLowerCase().includes('егэ')) {
        editReviewScoreInput.min = 0;
        editReviewScoreInput.max = 100;
        editReviewScoreInput.placeholder = 'Баллы от 0 до 100';
    }

    editReviewModalOverlay.style.display = 'flex';
}

function closeEditModal() {
    if (editReviewModalOverlay) {
        editReviewModalOverlay.style.display = 'none';
    }
}

async function saveReviewChangesHandler() {
    if (!editingReviewIdInput || !editReviewTextInput || !editReviewScoreInput) {
        console.error('Поля для сохранения изменений не найдены!');
        return;
    }

    const reviewId = editingReviewIdInput.value;
    const updatedReviewText = editReviewTextInput.value;
    const updatedScore = parseInt(editReviewScoreInput.value, 10);

    // Получаем текущий отзыв для проверки типа экзамена
    const card = document.querySelector(`[data-review-id="${reviewId}"]`);
    const examElement = card ? card.querySelector('.exam') : null;
    const examText = examElement ? examElement.textContent : '';
    const isOGE = examText.toLowerCase().includes('огэ');
    const isEGE = examText.toLowerCase().includes('егэ');

    // Проверяем валидность оценки в зависимости от типа экзамена
    if (isOGE && (isNaN(updatedScore) || updatedScore < 2 || updatedScore > 5)) {
        alert('Для ОГЭ оценка должна быть от 2 до 5.');
        return;
    } else if (isEGE && (isNaN(updatedScore) || updatedScore < 0 || updatedScore > 100)) {
        alert('Для ЕГЭ баллы должны быть от 0 до 100.');
        return;
    } else if (!isOGE && !isEGE) {
        if (isNaN(updatedScore) || updatedScore < 1 || updatedScore > 5) {
            alert('Пожалуйста, введите корректную оценку от 1 до 5.');
            return;
        }
    }

    try {
        const response = await fetch(`http://localhost:7777/reviews/${reviewId}`, {
            method: 'PATCH',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                review: updatedReviewText,
                result: updatedScore,
            }),
        });

        if (response.ok) {
            window.location.href = '/pages/profile/standart.html';
        } else {
            const errorData = await response.text();
            throw new Error(`Ошибка при сохранении отзыва: ${response.status} ${errorData}`);
        }
    } catch (error) {
        console.error('Ошибка при сохранении:', error);
        alert(`Не удалось сохранить изменения. ${error.message}`);
    }
}
// --- Конец кода для модального окна редактирования ---

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
    
    const editCardButton = document.createElement('button'); // Переименовал, чтобы не конфликтовать с editButton из scope выше, если он был
    editCardButton.className = 'edit-review';
    editCardButton.textContent = 'Редактировать';
    editCardButton.style.cssText = 'color: #E0407B; font-size: 0.9em; background: transparent; border: none; padding: 0; cursor: pointer;';
    editCardButton.onclick = () => openEditModal(review); // Передаем весь объект review

    rightButtonsSubContainer.appendChild(deleteButton);
    rightButtonsSubContainer.appendChild(editCardButton);

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
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOMContentLoaded event fired. Initializing modal elements...'); // Лог выполнения DOMContentLoaded

    editReviewModalOverlay = document.getElementById('editReviewModalOverlay');
    console.log('editReviewModalOverlay:', editReviewModalOverlay); // Лог для overlay

    editReviewModalContent = document.getElementById('editReviewModalContent');
    console.log('editReviewModalContent:', editReviewModalContent); // Лог для content

    editingReviewIdInput = document.getElementById('editingReviewId');
    console.log('editingReviewIdInput:', editingReviewIdInput); // Лог для hidden input id

    editReviewTextInput = document.getElementById('editReviewText');
    console.log('editReviewTextInput:', editReviewTextInput); // Лог для textarea

    editReviewScoreInput = document.getElementById('editReviewScore');
    console.log('editReviewScoreInput:', editReviewScoreInput); // Лог для input score

    cancelEditReviewButton = document.getElementById('cancelEditReview');
    console.log('cancelEditReviewButton:', cancelEditReviewButton); // Лог для cancel button

    saveReviewChangesButton = document.getElementById('saveReviewChanges');
    console.log('saveReviewChangesButton:', saveReviewChangesButton); // Лог для save button

    if (editReviewModalOverlay) {
        editReviewModalOverlay.addEventListener('click', function(event) {
            if (event.target === editReviewModalOverlay) {
                closeEditModal();
            }
        });
    } else {
        console.error('editReviewModalOverlay is null, cannot attach event listener.');
    }

    if (cancelEditReviewButton) {
        cancelEditReviewButton.addEventListener('click', closeEditModal);
    } else {
        console.error('cancelEditReviewButton is null, cannot attach event listener.');
    }

    if (saveReviewChangesButton) {
        saveReviewChangesButton.addEventListener('click', saveReviewChangesHandler);
    } else {
        console.error('saveReviewChangesButton is null, cannot attach event listener.');
    }

    loadUserReviews(); // Загружаем отзывы
}); 