function toggleMenu() {
    const menu = document.getElementById("dropdown");
    menu.classList.toggle("active");
}

document.addEventListener("click", function(event) {
    const menu = document.getElementById("dropdown");
    const menuButton = document.querySelector(".menu-button");
    
    if (menu.classList.contains("active") &&
        !menu.contains(event.target) &&
        !menuButton.contains(event.target)) {
        menu.classList.remove("active");
    }
});
document.addEventListener('DOMContentLoaded', function() {
  const buttons = document.querySelectorAll('.expand-btn');
  
  buttons.forEach(button => {
    button.addEventListener('click', function() {
      const targetId = this.getAttribute('data-target');
      const content = document.getElementById(targetId);
      
      if (!content) {
        console.error('Элемент с id="' + targetId + '" не найден!');
        return;
      }
      
      content.classList.toggle('active');
    });
  });
});

// Обработчик клика вне меню
document.addEventListener("click", function(event) {
  const menu = document.getElementById("dropdown");
  const menuButton = document.querySelector(".menu-button");
  
  if (menu && menu.classList.contains("active") &&
      !menu.contains(event.target) &&
      !menuButton.contains(event.target)) {
    menu.classList.remove("active");
  }
});

$(document).ready(function(){
    $('#phone-input').inputmask('+7(999)-999-9999');
});

$(document).ready(function() {
    $('#email-input').on('focus', function() {
        this.setAttribute('placeholder', this.getAttribute('data-placeholder-focus'));
    }).on('blur', function() {
        if(!this.value) {
            this.setAttribute('placeholder', 'Email');
        }
    });
});

$(document).ready(function() {
    $('.toggle-password').click(function() {
        const passwordInput = $(this).siblings('input');
        const icon = $(this).find('.eye-icon');
        
        if (passwordInput.attr('type') === 'password') {
            passwordInput.attr('type', 'text');
            icon.text('👁️'); 
        } else {
            passwordInput.attr('type', 'password');
            icon.text('🔒'); 
        }
    });
});

/*$(document).ready(function() {
    $('#submit-data').click(function() {

        const formData = {
            phone: $('#phone-input').val(),
            email: $('#email-input').val(),
            password: $('#password').val(),
            password_repeat: $('#password-repeat').val()
        };


        if (!formData.phone || !formData.password || !formData.password_repeat) {
            alert('Заполните все поля!');
            return;
        }

        $.ajax({
            url: '/register',
            method: 'POST',
            data: formData,
            success: function(response) {
                alert('Регистрация успешна!');
            },
            error: function() {
                alert('Ошибка отправки данных');
            }
        });

        console.log(formData);
        alert(`Данные для отправки:\nТелефон: ${formData.phone}\nEmail: ${formData.email}`);
    });
});

 */