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
  const TRUNCATION_LENGTH = 200; // Characters after which truncation occurs

  reviewContainers.forEach(container => {
    const reviewTextElement = container.querySelector('.review-text');

    // Skip if button exists or no text element
    if (container.querySelector('.read-more') || !reviewTextElement) {
      return;
    }

    const fullText = reviewTextElement.textContent.trim();

    // Ensure the element starts non-expanded
    reviewTextElement.classList.remove('expanded');
    // Store full text in a data attribute for easy access
    reviewTextElement.dataset.fullText = fullText;

    if (fullText.length > TRUNCATION_LENGTH) {
      const shortText = fullText.slice(0, TRUNCATION_LENGTH) + '...';
      reviewTextElement.dataset.shortText = shortText;
      reviewTextElement.textContent = shortText; // Initially display truncated text

      const readMoreBtn = document.createElement('button');
      readMoreBtn.className = 'read-more';
      readMoreBtn.textContent = 'Читать полностью';
      readMoreBtn.style.display = 'inline-block'; // Make the button visible
      // Append button to the container (parent of reviewTextElement)
      container.appendChild(readMoreBtn);

      readMoreBtn.addEventListener('click', () => {
        const isCurrentlyExpanded = reviewTextElement.classList.toggle('expanded');
        if (isCurrentlyExpanded) {
          reviewTextElement.textContent = reviewTextElement.dataset.fullText;
          readMoreBtn.textContent = 'Свернуть';
        } else {
          reviewTextElement.textContent = reviewTextElement.dataset.shortText;
          readMoreBtn.textContent = 'Читать полностью';
        }
      });
    } else {
      // If text is not long enough for truncation, ensure full text is displayed
      // and no 'shortText' data attribute is lingering.
      reviewTextElement.textContent = fullText;
      delete reviewTextElement.dataset.shortText; // Clean up
    }
  });
}

  const observer = new IntersectionObserver(entries => {
    if (entries[0].isIntersecting) loadItems();
  });

  observer.observe(sentinel);
  loadItems(); // первая загрузка