document.addEventListener('DOMContentLoaded', function() {
  const reviewContainers = document.querySelectorAll('.review-container');
  const MAX_LENGTH = 200; // Максимальная длина текста до обрезки
  
  reviewContainers.forEach(container => {
    const reviewText = container.querySelector('.review-text');
    const fullText = reviewText.textContent.trim();
    
    if (fullText.length > MAX_LENGTH) {
      // Сохраняем полный текст в data-атрибут
      reviewText.dataset.fullText = fullText;
      
      // Обрезаем текст и добавляем многоточие
      const shortText = fullText.substring(0, MAX_LENGTH) + '...';
      reviewText.textContent = shortText;
      reviewText.dataset.shortText = shortText;
      
      // Находим кнопку и показываем её
      const readMoreBtn = container.querySelector('.read-more');
      readMoreBtn.style.display = 'inline-block';
      
      // Добавляем обработчик клика
      readMoreBtn.addEventListener('click', function() {
        if (reviewText.classList.contains('collapsed')) {
          // Показываем полный текст
          reviewText.textContent = reviewText.dataset.fullText;
          reviewText.classList.remove('collapsed');
          readMoreBtn.textContent = 'Свернуть';
        } else {
          // Показываем сокращённый текст
          reviewText.textContent = reviewText.dataset.shortText;
          reviewText.classList.add('collapsed');
          readMoreBtn.textContent = 'Читать полностью';
        }
      });
    } else {
      // Если текст короткий, скрываем кнопку
      container.querySelector('.read-more').style.display = 'none';
    }
  });
});
// Параметры загрузки
let LIMIT = 8; // сначала загружаем 8 отзывов
const NEXT_LIMIT = 4; // потом по 4
let page = 1;
let loading = false;
let allLoaded = false;

const container = document.getElementById('container');
const sentinel = document.getElementById('sentinel');
const examType = document.body.getAttribute('data-exam');
const endpoint = document.body.getAttribute('data-endpoint');
const examName = (examType === "ege") ? "ЕГЭ" : "ОГЭ";

if (!endpoint) {
  console.error('Не указан эндпоинт для загрузки отзывов (data-endpoint)');
  sentinel.textContent = "Ошибка конфигурации";
}

async function loadItems() {
  if (loading || allLoaded || !endpoint) return;
  loading = true;

  try {
    const res = await fetch(`http://localhost:7777/${endpoint}?page=${page}&per_page=${LIMIT}`);
    
    // Если получили 404, значит отзывов нет
    if (res.status === 404) {
      sentinel.textContent = "Отзывов пока нет";
      allLoaded = true;
      return;
    }
    
    // Если другая ошибка (не 404) - это проблема сервера
    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }

    const data = await res.json();

    // Если данных меньше чем LIMIT - значит это последняя порция
    if (data.length < LIMIT) {
      allLoaded = true;
      sentinel.textContent = data.length === 0 ? "Больше отзывов нет" : "Больше отзывов нет.";
    }

    function formatDate(rawDateStr) {
      const cleaned = rawDateStr.replace(" +", "+").replace(/(\+|\-)(\d{2})(\d{2})/, "$1$2:$3");

      const date = new Date(cleaned);

      if (isNaN(date)) return "Некорректная дата";

      const day = String(date.getDate()).padStart(2, "0");
      const month = String(date.getMonth() + 1).padStart(2, "0");
      const year = date.getFullYear();

      return `${day}.${month}.${year}`;
    }

    data.forEach(item => {
      console.log(item.created_at)
      const card = document.createElement('div');
      card.className = 'card';
      card.innerHTML = `
        <div class="card-header">
          <div class="info">
            <div class="name">${item.name || "Аноним"}</div>
            <div class="exam">${examName}: <strong>${item.result}</strong></div>
            <div class="date">Дата публикации: <strong>${formatDate(item.created_at) || "Неизвестно"}</strong></div>
          </div>
          <img src="../../../assets/img/avatar.jpg" alt="Аватар" />
        </div>
        <div class="card-body">
          <div class="review-container">
            <div class="review-text">${item.review}</div>
          </div>
        </div>
      `;
      container.appendChild(card);
    });

    // Добавляем кнопки "Читать полностью"
    addReadMoreButtons();

    page++;
    LIMIT = NEXT_LIMIT;

  } catch (e) {
    sentinel.textContent = "Ошибка загрузки: сервер недоступен";
    console.error('Ошибка при загрузке отзывов:', e);
    allLoaded = true;  // Предотвращаем дальнейшие попытки загрузки при ошибке
  } finally {
    loading = false;
  }
}

// Функция добавления кнопок "Читать полностью"
function addReadMoreButtons() {
  const reviewContainers = document.querySelectorAll('.review-container');

  reviewContainers.forEach(container => {
    const reviewText = container.querySelector('.review-text');
    const readMoreBtn = container.querySelector('.read-more') || document.createElement('button');
    
    if (!container.querySelector('.read-more')) {
      readMoreBtn.className = 'read-more';
      readMoreBtn.textContent = 'Читать полностью';
      container.appendChild(readMoreBtn);
    }

    // Проверяем, нужна ли кнопка
    if (reviewText.scrollHeight > reviewText.clientHeight) {
      readMoreBtn.style.display = 'block';
      
      readMoreBtn.onclick = () => {
        if (reviewText.classList.contains('expanded')) {
          reviewText.classList.remove('expanded');
          readMoreBtn.textContent = 'Читать полностью';
        } else {
          reviewText.classList.add('expanded');
          readMoreBtn.textContent = 'Свернуть';
        }
      };
    } else {
      readMoreBtn.style.display = 'none';
    }
  });
}


const observer = new IntersectionObserver(entries => {
  if (entries[0].isIntersecting) loadItems();
});

observer.observe(sentinel);
loadItems(); // первая загрузка