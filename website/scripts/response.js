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