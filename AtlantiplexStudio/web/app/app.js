document.addEventListener('DOMContentLoaded', () => {
  const loginBtn = document.getElementById('login-btn');
  if (!loginBtn) return;
  loginBtn.addEventListener('click', async () => {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const status = document.getElementById('login-status');
    status.textContent = '';
    try {
      const res = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      if (!res.ok) {
        status.textContent = 'Login failed';
        return;
      }
      const data = await res.json();
      const token = data.token;
      localStorage.setItem('token', token);
      // Show stage UI and embed stage via iframe
      document.getElementById('login-section').style.display = 'none';
      const stageSection = document.getElementById('stage-section');
      stageSection.style.display = 'block';
      const stageFrame = document.getElementById('stage-frame');
      stageFrame.src = '/stage/?token=' + encodeURIComponent(token) + '&room=' + encodeURIComponent('default');
    } catch (err) {
      status.textContent = 'Network error';
    }
  });
});
