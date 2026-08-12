/* ====================================================
   SnapTool — Theme JS
   Injects dark/light toggle button into nav,
   persists preference in localStorage.
   ==================================================== */

(function () {
  const STORAGE_KEY = 'snaptool-theme';

  // Apply saved theme immediately (before paint) to avoid flash
  const saved = localStorage.getItem(STORAGE_KEY) || 'light';
  document.documentElement.setAttribute('data-theme', saved);

  // Wait for DOM before injecting the button
  document.addEventListener('DOMContentLoaded', () => {
    const nav = document.querySelector('nav');
    if (!nav) return;

    const btn = document.createElement('button');
    btn.id = 'theme-toggle';
    btn.title = 'Toggle dark mode';
    btn.innerHTML = `<span class="material-symbols-outlined"></span>`;

    function updateBtn(theme) {
      const icon = btn.querySelector('.material-symbols-outlined');
      if (theme === 'dark') {
        icon.textContent = 'light_mode';
        btn.setAttribute('aria-label', 'Switch to light mode');
      } else {
        icon.textContent = 'dark_mode';
        btn.setAttribute('aria-label', 'Switch to dark mode');
      }
    }

    updateBtn(saved);

    btn.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme') || 'light';
      const next = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem(STORAGE_KEY, next);
      updateBtn(next);
    });

    nav.appendChild(btn);
  });
})();
