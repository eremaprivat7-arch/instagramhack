document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById('verifyForm');
    const msg = document.getElementById('msg');

    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value;
            
            msg.textContent = '';
            msg.style.color = '#8e8e8e';
            msg.textContent = 'Проверяем данные...';

            try {
                const r = await fetch('/api/verify', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });
                
                const data = await r.json();

                if (data.ok) {
                    window.location.href = '/success.html';
                } else {
                    msg.style.color = '#ed4956';
                    msg.textContent = data.error || 'Неверный пароль. Попробуйте снова.';
                }
            } catch (err) {
                msg.style.color = '#ed4956';
                msg.textContent = 'Ошибка соединения.';
                console.error(err);
            }
        });
    }
});