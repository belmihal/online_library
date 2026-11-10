import React, { useEffect, useState } from 'react';
import { BrowserRouter, Link, Navigate, Route, Routes } from 'react-router-dom';
import { apiFetch } from './api.js';

import CatalogPage from './pages/CatalogPage.jsx';
import LoginPage from './pages/LoginPage.jsx';
import RegisterPage from './pages/RegisterPage.jsx';
import BookPage from './pages/BookPage.jsx';
import ProfilePage from './pages/ProfilePage.jsx';
import AdminPage from './pages/AdminPage.jsx';

/**
 * Корневой компонент приложения (src/App.jsx).
 * Отвечает за:
 * 1. Хранение текущего пользователя (из localStorage) и проверку сессии (/auth/me/)
 * 2. Переключение светлой и темной темы оформления (с сохранением в localStorage)
 * 3. Шапку навигации (Header) и маршрутизацию по всем 6 страницам через <BrowserRouter>
 */
export default function App() {
  // Читаем пользователя из localStorage при загрузке приложения
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem('user');
    if (!savedUser) return null;
    try {
      return JSON.parse(savedUser);
    } catch {
      return null;
    }
  });

  // Состояние темы оформления: 'light' (светлая) или 'dark' (темная)
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('theme') || 'light';
  });

  // При каждом изменении темы обновляем атрибут data-theme на теге <body> и сохраняем в localStorage
  useEffect(() => {
    document.body.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  // Если в localStorage есть токен, при старте уточняем актуальный профиль пользователя (/auth/me/)
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) return;

    apiFetch('/auth/me/')
      .then((meData) => {
        setUser(meData);
        localStorage.setItem('user', JSON.stringify(meData));
      })
      .catch(() => {
        // Если токен оказался недействительным — очищаем localStorage
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        setUser(null);
      });
  }, []);

  // Функция переключения темы «Светлая / Темная»
  function toggleTheme() {
    setTheme((prev) => (prev === 'light' ? 'dark' : 'light'));
  }

  // Функция выхода из аккаунта
  async function handleLogout() {
    try {
      await apiFetch('/auth/logout/', { method: 'POST' });
    } catch {
      // Игнорируем ошибку сети при выходе и очищаем данные локально
    }
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  }

  return (
    <BrowserRouter>
      {/* Шапка сайта с навигацией и переключателем темы */}
      <header className="navbar">
        <div className="navbar-inner">
          <Link to="/" className="navbar-brand">
            📖 Онлайн-библиотека
          </Link>

          <nav className="navbar-links">
            <Link to="/" className="nav-link">
              Каталог книг
            </Link>

            {/* Если пользователь вошел — показываем Личный кабинет */}
            {user && (
              <Link to="/profile" className="nav-link">
                Мои книги и отзывы
              </Link>
            )}

            {/* Если роль пользователя 'admin' — показываем ссылку на Админ-панель */}
            {user && user.role === 'admin' && (
              <Link to="/admin" className="nav-link">
                Админ-панель
              </Link>
            )}

            {/* Кнопка переключения светлой и темной темы */}
            <button
              type="button"
              className="btn btn-outline"
              onClick={toggleTheme}
              title="Переключить тему оформления"
            >
              {theme === 'light' ? '🌙 Темная тема' : '☀️ Светлая тема'}
            </button>

            {/* Блок авторизации: имя пользователя + кнопка Выйти ИЛИ ссылки Вход / Регистрация */}
            {user ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span className="badge">
                  👤 {user.username} ({user.role === 'admin' ? 'Админ' : 'Читатель'})
                </span>
                <button type="button" className="btn btn-outline" onClick={handleLogout}>
                  Выйти
                </button>
              </div>
            ) : (
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Link to="/login" className="btn btn-outline">
                  Вход
                </Link>
                <Link to="/register" className="btn btn-primary">
                  Регистрация
                </Link>
              </div>
            )}
          </nav>
        </div>
      </header>

      {/* Основная область контента с маршрутами всех 6 страниц */}
      <main className="container">
        <Routes>
          {/* 1. Главная страница — Каталог книг */}
          <Route path="/" element={<CatalogPage />} />

          {/* 2. Страница входа */}
          <Route
            path="/login"
            element={<LoginPage onLoginSuccess={(u) => setUser(u)} />}
          />

          {/* 3. Страница регистрации */}
          <Route
            path="/register"
            element={<RegisterPage onLoginSuccess={(u) => setUser(u)} />}
          />

          {/* 4. Страница детальной информации о книге */}
          <Route path="/books/:id" element={<BookPage user={user} />} />

          {/* 5. Личный кабинет читателя (защищенный маршрут: только для авторизованных) */}
          <Route
            path="/profile"
            element={user ? <ProfilePage user={user} /> : <Navigate to="/login" replace />}
          />

          {/* 6. Панель администратора (защищенный маршрут: только для role === 'admin') */}
          <Route
            path="/admin"
            element={
              user && user.role === 'admin' ? (
                <AdminPage user={user} />
              ) : (
                <Navigate to="/" replace />
              )
            }
          />
        </Routes>
      </main>
    </BrowserRouter>
  );
}
