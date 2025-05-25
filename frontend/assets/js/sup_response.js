document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('container');
    const sentinel = document.getElementById('sentinel');
    const examType = document.body.getAttribute('data-exam');
    const endpoint = document.body.getAttribute('data-endpoint');
    
    let page = 1;
    let loading = false;
    let hasMore = true;
    
    // Функция для создания карточки отзыва
    function createReviewCard(review) {
        const card = document.createElement('div');
        card.className = 'card';
        card.setAttribute('data-review-id', review.id); // Сохраняем ID отзыва
        
        card.innerHTML = `
            <div class="card-header">
                <div class="info">
                    <div class="name">${review.name}</div>
                    <div class="exam">${examType.toUpperCase()}: <strong>${review.score}</strong></div>
                    <div class="date">Дата публикации: <strong>${review.date}</strong></div>
                </div>
                <img src="${review.avatar || '../../../assets/img/avatar.jpg'}" alt="Аватар">
            </div>
            <div class="card-body">
                <div class="review-container">
                    <div class="review-text ${review.text.length > 200 ? '' : 'expanded'}">${review.text}</div>
                    ${review.text.length > 200 ? '<button class="read-more">Читать полностью</button>' : ''}
                    <button class="delete-button" onclick="deleteReview('${review.id}')">Удалить</button>
                </div>
            </div>
        `;

        // Добавляем обработчик для кнопки "Читать полностью"
        const readMoreBtn = card.querySelector('.read-more');
        if (readMoreBtn) {
            readMoreBtn.addEventListener('click', function() {
                const reviewText = this.previousElementSibling;
                reviewText.classList.toggle('expanded');
                this.textContent = reviewText.classList.contains('expanded') ? 'Свернуть' : 'Читать полностью';
            });
        }

        return card;
    }

    // Функция загрузки отзывов
    async function loadReviews() {
        if (loading || !hasMore) return;
        
        loading = true;
        sentinel.textContent = 'Загрузка...';
        
        try {
            // TODO: Замените на реальный API endpoint
            const response = await fetch(`/api/${endpoint}?page=${page}`);
            const data = await response.json();
            
            if (data.reviews.length === 0) {
                hasMore = false;
                sentinel.textContent = 'Отзывов пока нет';
                return;
            }
            
            data.reviews.forEach(review => {
                container.appendChild(createReviewCard(review));
            });
            
            page++;
            sentinel.textContent = 'Загрузка...';
            
        } catch (error) {
            console.error('Ошибка при загрузке отзывов:', error);
            sentinel.textContent = 'Ошибка загрузки';
        } finally {
            loading = false;
        }
    }

    // Функция удаления отзыва
    window.deleteReview = async function(reviewId) {
        if (!confirm('Вы уверены, что хотите удалить этот отзыв?')) {
            return;
        }

        try {
            // TODO: Замените на реальный API endpoint
            const response = await fetch(`/api/${endpoint}/${reviewId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const card = document.querySelector(`[data-review-id="${reviewId}"]`);
                if (card) {
                    card.remove();
                }
                // Если отзывов не осталось, показываем сообщение
                if (container.children.length === 0) {
                    sentinel.textContent = 'Отзывов пока нет';
                }
            } else {
                throw new Error('Ошибка при удалении отзыва');
            }
        } catch (error) {
            console.error('Ошибка при удалении отзыва:', error);
            alert('Не удалось удалить отзыв. Пожалуйста, попробуйте позже.');
        }
    };

    // Наблюдатель за прокруткой
    const observer = new IntersectionObserver(entries => {
        if (entries[0].isIntersecting && !loading) {
            loadReviews();
        }
    });

    observer.observe(sentinel);

    // Загружаем первую страницу
    loadReviews();
}); 