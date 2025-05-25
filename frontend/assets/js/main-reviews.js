document.addEventListener('DOMContentLoaded', async function() {
    const container = document.getElementById('container');
    const sentinel = document.getElementById('sentinel');

    async function loadMainPageReviews() {
        try {
            // Загружаем по одному отзыву каждого типа
            const [ogeResponse, egeResponse] = await Promise.all([
                fetch('http://localhost:7777/reviews/oge?page=1&per_page=1'),
                fetch('http://localhost:7777/reviews/ege?page=1&per_page=1')
            ]);

            if (!ogeResponse.ok && !egeResponse.ok) {
                throw new Error('Ошибка загрузки отзывов');
            }

            const [ogeData, egeData] = await Promise.all([
                ogeResponse.ok ? ogeResponse.json() : [],
                egeResponse.ok ? egeResponse.json() : []
            ]);

            function formatDate(rawDateStr) {
                const cleaned = rawDateStr.replace(" +", "+").replace(/(\+|\-)(\d{2})(\d{2})/, "$1$2:$3");
                const date = new Date(cleaned);
                if (isNaN(date)) return "Некорректная дата";
                const day = String(date.getDate()).padStart(2, "0");
                const month = String(date.getMonth() + 1).padStart(2, "0");
                const year = date.getFullYear();
                return `${day}.${month}.${year}`;
            }

            function createReviewCard(item, examName) {
                const card = document.createElement('div');
                card.className = 'card';
                card.innerHTML = `
                    <div class="card-header">
                        <div class="info">
                            <div class="name">Имя: <strong>${item.name || "Аноним"}</strong></div>
                            <div class="exam">${examName}: <strong>${item.result}</strong></div>
                            <div class="date">Дата публикации: <strong>${formatDate(item.created_at) || "Неизвестно"}</strong></div>
                        </div>
                        <img src="assets/img/avatar.jpg" alt="Аватар" />
                    </div>
                    <div class="card-body">
                        <div class="review-container">
                            <div class="review-text">${item.review}</div>
                            <button class="read-more">Читать полностью</button>
                        </div>
                    </div>
                `;
                return card;
            }

            // Добавляем отзывы в контейнер
            if (ogeData.length > 0) {
                container.appendChild(createReviewCard(ogeData[0], "ОГЭ"));
            }
            if (egeData.length > 0) {
                container.appendChild(createReviewCard(egeData[0], "ЕГЭ"));
            }

            // Скрываем sentinel после загрузки
            sentinel.style.display = 'none';

            // Добавляем обработчики для кнопок
            initializeReadMoreButtons();

        } catch (error) {
            console.error('Ошибка при загрузке отзывов:', error);
            sentinel.textContent = "Ошибка загрузки отзывов";
        }
    }

    // Функция инициализации кнопок "Читать полностью"
    function initializeReadMoreButtons() {
        const buttons = document.querySelectorAll('.read-more');
        buttons.forEach(button => {
            const reviewText = button.previousElementSibling;
            
            // Показываем кнопку только если текст не помещается
            if (reviewText.scrollHeight > reviewText.clientHeight) {
                button.style.display = 'inline-block';
                
                button.addEventListener('click', () => {
                    const isExpanded = reviewText.classList.contains('expanded');
                    reviewText.classList.toggle('expanded');
                    button.textContent = isExpanded ? 'Читать полностью' : 'Свернуть';
                });
            } else {
                button.style.display = 'none';
            }
        });
    }

    // Загружаем отзывы при загрузке страницы
    loadMainPageReviews();
}); 