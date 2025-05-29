document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('container');
    const sentinel = document.getElementById('sentinel');
    const endpoint = document.body.getAttribute('data-endpoint');
    const API_BASE_URL = 'http://localhost:7777';
    
    let page = 1;
    let loading = false;
    let hasMore = true;
    
    // Функция для форматирования даты
    function formatDate(dateString) {
        const cleaned = dateString.replace(" +", "+").replace(/(\+|\-)(\d{2})(\d{2})/, "$1$2:$3");
        const date = new Date(cleaned);
        
        if (isNaN(date)) return "Некорректная дата";
        
        const day = String(date.getDate()).padStart(2, "0");
        const month = String(date.getMonth() + 1).padStart(2, "0");
        const year = date.getFullYear();
        
        return `${day}.${month}.${year}`;
    }
    
    // Добавляем стили для текста отзыва и кнопок
    const style = document.createElement('style');
    style.textContent = `
        .review-text {
            color: #ffffff;
            max-height: 100px;
            overflow: hidden;
            transition: all 0.3s ease;
            line-height: 1.5;
        }
        .review-text.expanded {
            max-height: none;
        }
        .review-text.collapsed {
            max-height: 100px;
            overflow: hidden;
        }
        .button-container {
            display: flex;
            justify-content: flex-start;
            align-items: center;
            margin-top: 10px;
            gap: 10px;
        }
        .read-more {
            display: inline-block;
            background: none;
            border: none;
            color: #d83787;
            cursor: pointer;
            font-family: inherit;
            font-size: 16px;
            padding: 0;
            margin-right: auto;
        }
        .read-more:hover {
            text-decoration: underline;
        }
        .delete-button {
            display: inline-block;
            background: none;
            border: none;
            color: #ff4444;
            cursor: pointer;
            font-family: inherit;
            font-size: 16px;
            padding: 0;
        }
        .delete-button:hover {
            color: #ff0000;
            text-decoration: underline;
        }
    `;
    document.head.appendChild(style);

    // Функция для создания карточки отзыва
    function createReviewCard(review) {
        const card = document.createElement('div');
        card.className = 'card';
        card.setAttribute('data-review-id', review.id);
        
        // Определяем, нужна ли кнопка "Читать полностью"
        const needsReadMore = review.review.length > 200;
        
        card.innerHTML = `
            <div class="card-header">
                <div class="info">
                    <div class="name">${review.name || "Аноним"}</div>
                    <div class="exam">${review.exam}: <strong>${review.result}</strong></div>
                    <div class="date">Дата публикации: <strong>${formatDate(review.created_at)}</strong></div>
                </div>
                <img src="${review.avatar_url || '../../../assets/img/avatar.jpg'}" alt="Аватар" />
            </div>
            <div class="card-body">
                <div class="review-container">
                    <div class="review-text ${needsReadMore ? 'collapsed' : ''}">${review.review}</div>
                    <div class="button-container">
                        <button class="read-more" style="display: ${needsReadMore ? 'inline-block' : 'none'}">Читать полностью</button>
                    </div>
                </div>
                <button class="delete-button" onclick="deleteReview('${review.id}')">Удалить</button>
            </div>
        `;

        // Добавляем обработчик для кнопки "Читать полностью"
        const readMoreBtn = card.querySelector('.read-more');
        const reviewText = card.querySelector('.review-text');

        if (readMoreBtn && needsReadMore) {
            readMoreBtn.addEventListener('click', function() {
                reviewText.classList.toggle('expanded');
                reviewText.classList.toggle('collapsed');
                this.textContent = reviewText.classList.contains('collapsed') ? 'Читать полностью' : 'Свернуть';
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
            const response = await fetch(`${API_BASE_URL}/${endpoint}?page=${page}`, {
                headers: {
                    'Accept': 'application/json'
                },
                credentials: 'include'
            });

            // Если получили 404, значит отзывов больше нет
            if (response.status === 404) {
                hasMore = false;
                sentinel.textContent = page === 1 ? 'Отзывов пока нет' : 'Больше отзывов нет';
                return;
            }

            if (!response.ok) {
                throw new Error('Ошибка загрузки отзывов');
            }
            
            const data = await response.json();
            
            // Если пришел пустой массив или не массив вообще
            if (!Array.isArray(data) || data.length === 0) {
                hasMore = false;
                sentinel.textContent = page === 1 ? 'Отзывов пока нет' : 'Больше отзывов нет';
                return;
            }
            
            data.forEach(review => {
                container.appendChild(createReviewCard(review));
            });
            
            page++;

            // Если загрузили меньше, чем ожидалось, значит это последняя страница
            if (data.length < 10) { // предполагаем, что сервер возвращает по 10 отзывов
                hasMore = false;
                sentinel.textContent = 'Больше отзывов нет';
            } else {
                sentinel.textContent = ''; // Очищаем текст, если есть еще отзывы
            }
            
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
            const response = await fetch(`${API_BASE_URL}/${endpoint}/${reviewId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                credentials: 'include'
            });

            if (response.ok) {
                // После успешного удаления перезагружаем страницу
                window.location.reload();
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