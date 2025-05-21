document.addEventListener('DOMContentLoaded', function() {
    const reviewContainers = document.querySelectorAll('.review-container');
    
    reviewContainers.forEach(container => {
        const reviewText = container.querySelector('.review-text');
        const fullText = reviewText.textContent.trim();
        
        // Создаем кнопку
        const readMoreBtn = document.createElement('button');
        readMoreBtn.className = 'read-more';
        readMoreBtn.textContent = 'Читать полностью';
        container.appendChild(readMoreBtn);
        
        if (fullText.length > 100) {
            // Добавляем класс для усеченного текста
            reviewText.classList.add('truncated');
            
            // Показываем кнопку
            readMoreBtn.style.display = 'inline-block';
            
            // Обработчик клика
            readMoreBtn.addEventListener('click', function() {
                if (reviewText.style.maxHeight) {
                    reviewText.style.maxHeight = null;
                    this.textContent = 'Читать полностью';
                    reviewText.classList.add('truncated');
                } else {
                    reviewText.style.maxHeight = 'none';
                    this.textContent = 'Свернуть';
                    reviewText.classList.remove('truncated');
                }
            });
        }
    });
});
function toggleMenu() {
    var menu = document.getElementById("dropdown");
    menu.classList.toggle("active");
}