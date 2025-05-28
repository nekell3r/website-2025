// Функция для форматирования даты
function formatPurchaseDate(dateString) {
    const date = new Date(dateString);
    return `Дата покупки: ${date.toLocaleDateString('ru-RU')}`;
}

// Функция для определения изображения продукта
function getProductImage(productName) {
    const name = productName.toLowerCase();
    if (name === 'егэ') {
        return '../../assets/img/work_note3.png';
    } else if (name === 'огэ') {
        return '../../assets/img/work_note4.png';
    }
    return '../../assets/img/work_note3.png'; // Дефолтное изображение
}

// Функция для создания карточки продукта
function createPurchaseCard(purchase) {
    const card = document.createElement('div');
    card.className = 'purchase-card';
    card.innerHTML = `
        <img src="${getProductImage(purchase.name)}" alt="${purchase.name}">
        <div class="purchase-info">
            <div class="purchase-date">${formatPurchaseDate(purchase.paid_at)}</div>
            <h3 class="purchase-title">${purchase.name}</h3>
        </div>
    `;

    card.addEventListener('click', () => openProductModal(purchase));
    return card;
}

// Функция для открытия модального окна продукта
function openProductModal(product) {
    const modal = document.getElementById('productModalOverlay');
    const title = document.getElementById('productModalTitle');
    const description = document.getElementById('productModalDescription');
    const downloadLink = document.getElementById('productModalDownload');

    title.textContent = product.name;
    description.textContent = product.description;
    downloadLink.href = product.download_link;

    modal.style.display = 'flex';

    // Добавляем обработчик клика вне модального окна
    modal.addEventListener('click', (event) => {
        if (event.target === modal) {
            closeProductModal();
        }
    });
}

// Функция для закрытия модального окна продукта
function closeProductModal() {
    const modal = document.getElementById('productModalOverlay');
    modal.style.display = 'none';
}

// Функция для загрузки купленных продуктов
async function loadPurchases() {
    try {
        const response = await fetch('http://localhost:7777/me/purchases', {
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
            throw new Error(`Ошибка при загрузке покупок: ${response.statusText}`);
        }

        const purchases = await response.json();
        const container = document.getElementById('purchasesContainer');
        
        if (!container) {
            console.error('Контейнер для покупок не найден');
            return;
        }

        container.innerHTML = '';

        if (purchases.length === 0) {
            container.innerHTML = '<p style="color: #fff; text-align: center;">У вас пока нет купленных продуктов.</p>';
            return;
        }

        purchases.forEach(purchase => {
            const card = createPurchaseCard(purchase);
            container.appendChild(card);
        });

    } catch (error) {
        console.error('Ошибка:', error);
        const container = document.getElementById('purchasesContainer');
        if (container) {
            container.innerHTML = '<p style="color: #ff6b6b; text-align: center;">Не удалось загрузить информацию о покупках. Пожалуйста, попробуйте позже.</p>';
        }
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    // Загружаем покупки при загрузке страницы
    loadPurchases();
}); 