



        document.getElementById("send-phone").addEventListener("click", function () {
            const phoneInput = document.getElementById("phone-input");
            const rawPhone = phoneInput.value.trim();
            const cleanedPhone = rawPhone.replace(/\D/g, '');
            const errorDiv = document.getElementById("phone-error");

            if (!cleanedPhone) {
                errorDiv.textContent = "Введите номер телефона.";
                return;
            } else if (cleanedPhone.length !== 11 || !/^7\d{10}$/.test(cleanedPhone)) {
                errorDiv.textContent = "Формат: +7 (XXX) XXX-XX-XX";
                return;
            } else {
                errorDiv.textContent = "";
            }

            fetch("https://a824-185-153-181-236.ngrok-free.app/auth/register/phone_code", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ phone: "+" + cleanedPhone })
            })
            .then(async res => {
                if (!res.ok) {
                    const errorData = await res.json();
                    throw new Error(errorData?.detail || `Ошибка: ${res.status}`);
                }
                return res.json();
            })
            .then(data => {
                errorDiv.style.color = "green";
                errorDiv.textContent = "Код отправлен!";
            })
            .catch(err => {
                errorDiv.style.color = "red";
                errorDiv.textContent = err.message || "Не удалось отправить код.";
            });
        });

        document.getElementById("send-email").addEventListener("click", function () {
            const emailInput = document.getElementById("email-input");
            const email = emailInput.value.trim();
            const errorDiv = document.getElementById("email-error");
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

            if (!email) {
                errorDiv.textContent = "Введите email.";
                return;
            } else if (!emailRegex.test(email)) {
                errorDiv.textContent = "Неверный формат email.";
                return;
            } else {
                errorDiv.textContent = "";
            }

            fetch("https://a824-185-153-181-236.ngrok-free.app/auth/register/email_code", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email: email })
            })
            .then(async res => {
                if (!res.ok) {
                    const errorData = await res.json();
                    throw new Error(errorData?.detail || `Ошибка: ${res.status}`);
                }
                return res.json();
            })
            .then(data => {
                errorDiv.style.color = "green";
                errorDiv.textContent = "Код отправлен на email!";
            })
            .catch(err => {
                errorDiv.style.color = "red";
                errorDiv.textContent = err.message || "Не удалось отправить код.";
            });
        });

        document.getElementById("submit-data").addEventListener("click", async () => {
            const rawPhone = document.getElementById("phone-input")?.value.trim();
            const cleanedPhone = rawPhone.replace(/\D/g, '');
            const email = document.getElementById("email-input")?.value.trim();
            const codePhone = document.getElementById("code-phone")?.value.trim();
            const codeEmail = document.getElementById("code-email")?.value.trim();
            const password = document.getElementById("password")?.value;
            const passwordRepeat = document.getElementById("password-repeat")?.value;

            const errorBlock = document.getElementById("submit-error");
            errorBlock.textContent = "";

            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

            if (!cleanedPhone || cleanedPhone.length !== 11 || !/^7\d{10}$/.test(cleanedPhone)) {
                errorBlock.textContent = "Введите корректный номер телефона.";
                return;
            }
            if (email && !emailRegex.test(email)) {
                errorBlock.textContent = "Некорректный email.";
                return;
            }
            if (!codePhone) {
                errorBlock.textContent = "Введите код для телефона.";
                return;
            }
            if (email && !codeEmail) {
                errorBlock.textContent = "Введите код для email.";
                return;
            }
            if (!password || password.length < 8) {
                errorBlock.textContent = "Пароль должен содержать минимум 8 символов.";
                return;
            }
            if (password !== passwordRepeat) {
                errorBlock.textContent = "Пароли не совпадают.";
                return;
            }

            const payload = {
                phone: "+" + cleanedPhone,
                code_phone: codePhone,
                password: password,
                password_repeat: passwordRepeat
            };

            if (email) {
                payload.email = email;
                payload.code_email = codeEmail;
            }

            try {
                const response = await fetch("https://a824-185-153-181-236.ngrok-free.app/auth/register/verify", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    errorBlock.textContent = errorData.detail || "Произошла ошибка при регистрации.";
                } else {
                    window.location.href = "login.html";
                }
            } catch (err) {
                errorBlock.textContent = `Ошибка регистрации: ${err.message}`;
            }
        });