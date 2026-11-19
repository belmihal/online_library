/**
 * Общий скрипт макета страниц LitHub (js/layout.js).
 * Автоматически рисует:
 * 1. Шапку (<header id="app-header">) с логотипом «Lit [hub]», ссылками разделов,
 *    подсветкой активного пункта меню, переключателем темы и блоком авторизации.
 * 2. Минималистичный подвал (<footer id="app-footer">) ТОЛЬКО с контактами администраторов.
 */

(function () {
  const savedTheme = localStorage.getItem('theme') || 'light';
  document.body.setAttribute('data-theme', savedTheme);

  document.addEventListener('DOMContentLoaded', function () {
    renderHeader();
    renderFooter();
    syncCurrentUserSession();
  });

  // Определяем текущий открытый HTML-файл для подсветки активного пункта меню
  function getCurrentPageFile() {
    const pathname = window.location.pathname || '';
    const file = pathname.substring(pathname.lastIndexOf('/') + 1);
    return file === '' ? 'index.html' : file;
  }

  function navLinkHtml(href, label, currentFile) {
    const isActive = currentFile === href;
    const cls = isActive ? 'nav-link nav-link-active' : 'nav-link';
    return '<a href="' + href + '" class="' + cls + '">' + label + '</a>';
  }

  function renderHeader() {
    const headerEl = document.getElementById('app-header');
    if (!headerEl) return;

    const user = getCurrentUser();
    const currentFile = getCurrentPageFile();
    const currentTheme = document.body.getAttribute('data-theme') || 'light';
    const themeLabel = currentTheme === 'light' ? '🌙 Темная тема' : '☀️ Светлая тема';

    let navLinksHtml = '';
    navLinksHtml += navLinkHtml('index.html', 'Каталог', currentFile);
    navLinksHtml += navLinkHtml('collections.html', 'Подборки', currentFile);
    navLinksHtml += navLinkHtml('search.html', 'Поиск и категории', currentFile);

    if (user) {
      navLinksHtml += navLinkHtml('profile.html', 'Моя полка и отзывы', currentFile);
    }

    if (user && user.role === 'admin') {
      navLinksHtml += navLinkHtml('admin.html', 'Админ-панель', currentFile);
    }

    navLinksHtml +=
      '<button type="button" id="theme-toggle-btn" class="btn btn-outline" title="Переключить тему">' +
      themeLabel +
      '</button>';

    if (user) {
      const roleText = user.role === 'admin' ? 'Админ' : 'Читатель';
      navLinksHtml +=
        '<div style="display:flex;align-items:center;gap:10px;">' +
        '<span class="badge">👤 ' +
        escapeHtml(user.username) +
        ' (' +
        roleText +
        ')</span>' +
        '<button type="button" id="logout-btn" class="btn btn-outline">Выйти</button>' +
        '</div>';
    } else {
      navLinksHtml +=
        '<div style="display:flex;align-items:center;gap:8px;">' +
        '<a href="login.html" class="btn btn-outline">Вход</a>' +
        '<a href="register.html" class="btn btn-primary">Регистрация</a>' +
        '</div>';
    }

    headerEl.className = 'navbar';
    headerEl.innerHTML =
      '<div class="navbar-inner">' +
      '<a href="index.html" class="navbar-brand" aria-label="LitHub — На главную">' +
      '<span class="brand-lit">Lit</span>' +
      '<span class="brand-hub">hub</span>' +
      '</a>' +
      '<nav class="navbar-links">' +
      navLinksHtml +
      '</nav>' +
      '</div>';

    const themeBtn = document.getElementById('theme-toggle-btn');
    if (themeBtn) {
      themeBtn.addEventListener('click', function () {
        const now = document.body.getAttribute('data-theme') || 'light';
        const next = now === 'light' ? 'dark' : 'light';
        document.body.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
        themeBtn.textContent = next === 'light' ? '🌙 Темная тема' : '☀️ Светлая тема';
      });
    }

    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
      logoutBtn.addEventListener('click', async function () {
        try {
          await apiFetch('/auth/logout/', { method: 'POST' });
        } catch (e) {
          // Игнорируем сетевую ошибку при выходе
        }
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = 'index.html';
      });
    }
  }

  function renderFooter() {
    const footerEl = document.getElementById('app-footer');
    if (!footerEl) return;

    footerEl.className = 'site-footer';
    footerEl.innerHTML =
      '<div class="site-footer-inner">' +
      '<h3 class="footer-title">Контакты администраторов</h3>' +
      '<ul class="footer-contacts">' +
      '<li><strong>Главный администратор:</strong> <a href="mailto:admin@lithub.local">admin@lithub.local</a></li>' +
      '<li><strong>Техподдержка читателей:</strong> <a href="mailto:support@lithub.local">support@lithub.local</a></li>' +
      '<li><strong>Telegram:</strong> @lithub_admin</li>' +
      '<li><strong>Телефон:</strong> +7 (800) 555-35-35 (ежедневно с 09:00 до 21:00)</li>' +
      '</ul>' +
      '</div>';
  }

  function syncCurrentUserSession() {
    const token = localStorage.getItem('token');
    if (!token) return;

    apiFetch('/auth/me/')
      .then(function (meData) {
        const prevRaw = localStorage.getItem('user');
        const nextRaw = JSON.stringify(meData);
        if (prevRaw !== nextRaw) {
          localStorage.setItem('user', nextRaw);
          renderHeader();
        }
      })
      .catch(function () {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        renderHeader();
      });
  }

  function escapeHtml(text) {
    return String(text || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }
})();
