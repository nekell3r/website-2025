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
function createProductCard(product) {
    const card = document.createElement('div');
    card.className = 'purchase-card';
    card.setAttribute('data-product-id', product.id);
    card.innerHTML = `
        <img src="${getProductImage(product.name)}" alt="${product.name}">
        <div class="purchase-info">
            <h3 class="purchase-title">${product.name}</h3>
            <p class="purchase-price">${product.price} ₽</p>
        </div>
    `;

    card.addEventListener('click', () => openProductModal(product));
    return card;
}

// Функция для открытия модального окна редактирования продукта
function openProductModal(product) {
    const modal = document.getElementById('productModalOverlay');
    const name = document.getElementById('productName');
    const price = document.getElementById('productPrice');
    const description = document.getElementById('productDescription');
    const link = document.getElementById('productLink');
    const productId = document.getElementById('editingProductId');
    const productSlug = document.getElementById('editingProductSlug');

    name.value = product.name || '';
    price.value = product.price || '';
    description.value = product.description || '';
    link.value = product.download_link || '';
    productId.value = product.id || '';
    productSlug.value = product.slug || '';

    modal.style.display = 'flex';

    // Добавляем обработчик клика вне модального окна
    modal.addEventListener('click', (event) => {
        if (event.target === modal) {
            closeProductModal();
        }
    });
}

// Функция для закрытия модального окна
function closeProductModal() {
    const modal = document.getElementById('productModalOverlay');
    modal.style.display = 'none';
}

// Функция для сохранения изменений продукта
async function saveProductChanges() {
    const productSlug = document.getElementById('editingProductSlug').value;
    const name = document.getElementById('productName').value;
    const price = document.getElementById('productPrice').value;
    const description = document.getElementById('productDescription').value;
    const downloadLink = document.getElementById('productLink').value;

    try {
        const response = await fetch(`http://localhost:7777/admin/products/${productSlug}`, {
            method: 'PATCH',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                price: parseInt(price),
                description: description,
                download_link: downloadLink
            })
        });

        if (!response.ok) {
            throw new Error('Ошибка при сохранении изменений');
        }

        // Закрываем модальное окно и обновляем список продуктов
        closeProductModal();
        loadProducts();

    } catch (error) {
        console.error('Ошибка при сохранении:', error);
        alert('Не удалось сохранить изменения. Пожалуйста, попробуйте позже.');
    }
}

// Функция для загрузки продуктов
async function loadProducts() {
    try {
        const response = await fetch('http://localhost:7777/admin/products', {
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
            throw new Error(`Ошибка при загрузке продуктов: ${response.statusText}`);
        }

        const products = await response.json();
        const container = document.getElementById('productsContainer');
        
        if (!container) {
            console.error('Контейнер для продуктов не найден');
            return;
        }

        container.innerHTML = '';

        if (products.length === 0) {
            container.innerHTML = '<p style="color: #fff; text-align: center;">Нет доступных материалов.</p>';
            return;
        }

        products.forEach(product => {
            const card = createProductCard(product);
            container.appendChild(card);
        });

    } catch (error) {
        console.error('Ошибка при загрузке продуктов:', error);
        const container = document.getElementById('productsContainer');
        if (container) {
            container.innerHTML = '<p style="color: #ff6b6b; text-align: center;">Не удалось загрузить информацию о материалах. Пожалуйста, попробуйте позже.</p>';
        }
    }
}

// Загружаем продукты при загрузке страницы
document.addEventListener('DOMContentLoaded', loadProducts); 