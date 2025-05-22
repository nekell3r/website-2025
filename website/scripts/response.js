function toggleMenu() {
    const menu = document.getElementById("dropdown");
    menu.classList.toggle("active");
  }

  // Закрытие меню при клике вне него
  document.addEventListener("click", function (event) {
    const menu = document.getElementById("dropdown");
    const button = document.querySelector(".hamburger-button");

    const isClickInsideMenu = menu.contains(event.target);
    const isClickOnButton = button.contains(event.target);

    if (!isClickInsideMenu && !isClickOnButton && menu.classList.contains("active")) {
      menu.classList.remove("active");
    }
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
  const examName = (examType === "ege") ? "ЕГЭ" : "ОГЭ";

  async function loadItems() {
    if (loading || allLoaded) return;
    loading = true;

    try {
      const res = await fetch(`http://localhost:7777/reviews?page=${page}&per_page=${LIMIT}`);
      const data = await res.json();

      if (data.length < LIMIT) {
        allLoaded = true;
        sentinel.textContent = "Больше отзывов нет.";
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
            <img src="img/avatar.jpg" alt="Аватар" />
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
      sentinel.textContent = "Ошибка загрузки.";
      console.error(e);
    } finally {
      loading = false;
    }
  }

  // Функция добавления кнопок "Читать полностью"
  function addReadMoreButtons() {
  const reviewContainers = document.querySelectorAll('.review-container');

  reviewContainers.forEach(container => {
    const reviewText = container.querySelector('.review-text');

    // Не добавлять кнопку дважды
    if (container.querySelector('.read-more')) return;

    const readMoreBtn = document.createElement('button');
    readMoreBtn.className = 'read-more';
    readMoreBtn.textContent = 'Читать полностью';
    container.appendChild(readMoreBtn);

    const maxHeight = 150; // px

    if (reviewText.scrollHeight > maxHeight) {
      // Изначально текст с ограничением
      reviewText.style.maxHeight = maxHeight + 'px';
      reviewText.style.overflow = 'hidden';

      readMoreBtn.style.display = 'inline-block';

      readMoreBtn.addEventListener('click', () => {
        if (reviewText.classList.contains('expanded')) {
          // Сворачиваем
          reviewText.classList.remove('expanded');
          readMoreBtn.textContent = 'Читать полностью';
        } else {
          // Разворачиваем
          reviewText.classList.add('expanded');
          readMoreBtn.textContent = 'Свернуть';
        }
      });
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